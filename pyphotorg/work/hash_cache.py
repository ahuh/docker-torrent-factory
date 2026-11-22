import hashlib
import os
import sqlite3


# This path is backed by the persistent Docker volume.
DEFAULT_CACHE_PATH = "/cache/dedup_hashes.sqlite3"
# Read media in larger blocks to reduce per-read overhead.
HASH_BLOCK_SIZE = 1024 * 1024


def _file_signature(file_stat: os.stat_result) -> tuple[int, int, int, int, int]:
    """Return file metadata used to decide whether a cached hash is still valid."""
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
        file_stat.st_ctime_ns,
    )


class HashCache:
    """Persist SHA-256 hashes for files that may be duplicates."""

    def __init__(self, cache_path: str | None = None):
        """Open the cache database and create its table if needed."""
        self.cache_path = cache_path or os.getenv("DEDUP_CACHE_PATH", DEFAULT_CACHE_PATH)
        os.makedirs(os.path.dirname(os.path.abspath(self.cache_path)), exist_ok=True)
        # Connect to DB, create the DB file if it does not exist
        self.connection = sqlite3.connect(self.cache_path, timeout=30)
        # Create the cache table on first use.
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS file_hashes (
                path TEXT PRIMARY KEY,
                device INTEGER NOT NULL,
                inode INTEGER NOT NULL,
                size INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                ctime_ns INTEGER NOT NULL,
                digest TEXT NOT NULL
            )
            """
        )
        self.connection.commit()
        # Keep new hashes in memory until all media reads are complete.
        self.pending_entries = []

    def get_hash(self, file_path: str, file_stat: os.stat_result) -> str | None:
        """Return a cached hash only when the file metadata still matches."""
        path = os.path.abspath(file_path)
        signature = _file_signature(file_stat)
        row = self.connection.execute(
            """
            SELECT device, inode, size, mtime_ns, ctime_ns, digest
            FROM file_hashes
            WHERE path = ?
            """,
            (path,),
        ).fetchone()
        if row is None or tuple(row[:5]) != signature:
            return None
        return row[5]

    def hash_file(self, file_path: str, file_stat: os.stat_result) -> tuple[str, bool]:
        """Return a cached hash or calculate and queue a new SHA-256 hash."""
        cached_hash = self.get_hash(file_path, file_stat)
        if cached_hash is not None:
            return cached_hash, True

        digest = hashlib.sha256()
        with open(file_path, "rb") as media_file:
            while True:
                block = media_file.read(HASH_BLOCK_SIZE)
                if not block:
                    break
                digest.update(block)

        if _file_signature(os.stat(file_path)) != _file_signature(file_stat):
            raise OSError("File changed while its hash was being calculated")

        self.pending_entries.append(
            (os.path.abspath(file_path), *_file_signature(file_stat), digest.hexdigest())
        )
        return digest.hexdigest(), False

    def flush(self) -> None:
        """Write all queued hashes to the database in one transaction."""
        if not self.pending_entries:
            return
        # Batch writes so hashing does not hold a database write lock.
        self.connection.executemany(
            """
            INSERT INTO file_hashes
                (path, device, inode, size, mtime_ns, ctime_ns, digest)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                device = excluded.device,
                inode = excluded.inode,
                size = excluded.size,
                mtime_ns = excluded.mtime_ns,
                ctime_ns = excluded.ctime_ns,
                digest = excluded.digest
            """,
            self.pending_entries,
        )
        self.connection.commit()
        self.pending_entries.clear()

    def clear(self) -> int:
        """Delete all cached hashes and reclaim the database space they used."""
        self.flush()
        cursor = self.connection.execute("DELETE FROM file_hashes")
        deleted_count = cursor.rowcount
        self.connection.commit()
        # Shrink the database after deleting its rows.
        self.connection.execute("VACUUM")
        return deleted_count

    def close(self) -> None:
        """Flush queued hashes and close the database connection."""
        self.flush()
        self.connection.close()

    def __enter__(self):
        """Return this cache for use in a with block."""
        return self

    def __exit__(self, exception_type, exception, traceback):
        """Close the database when leaving a with block."""
        self.close()
