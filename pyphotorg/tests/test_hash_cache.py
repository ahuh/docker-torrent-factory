import contextlib
import hashlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

# Make the app's script modules importable when tests run from pyphotorg/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "work"))

from hash_cache import HashCache
from manual_clean_cache import main as clean_cache


class HashCacheTests(unittest.TestCase):
    def test_hash_persists_and_is_reused_for_unchanged_file(self):
        """Hash unchanged files once and reuse their hashes on later runs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "cache.sqlite3")
            file_path = os.path.join(temp_dir, "photo.jpg")
            with open(file_path, "wb") as media_file:
                media_file.write(b"photo-data")

            with HashCache(cache_path) as cache:
                first_hash, was_cached = cache.hash_file(file_path, os.stat(file_path))
                self.assertFalse(was_cached)

            with HashCache(cache_path) as cache:
                second_hash, was_cached = cache.hash_file(file_path, os.stat(file_path))
                self.assertTrue(was_cached)

            self.assertEqual(first_hash, second_hash)
            self.assertEqual(first_hash, hashlib.sha256(b"photo-data").hexdigest())

    def test_changed_file_invalidates_cached_hash(self):
        """Recalculate a hash when the file content and metadata change."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "cache.sqlite3")
            file_path = os.path.join(temp_dir, "photo.jpg")
            with open(file_path, "wb") as media_file:
                media_file.write(b"photo-data")

            with HashCache(cache_path) as cache:
                first_hash, _ = cache.hash_file(file_path, os.stat(file_path))

            with open(file_path, "wb") as media_file:
                media_file.write(b"other-data")
            with HashCache(cache_path) as cache:
                second_hash, was_cached = cache.hash_file(file_path, os.stat(file_path))

            self.assertFalse(was_cached)
            self.assertNotEqual(first_hash, second_hash)
            self.assertEqual(second_hash, hashlib.sha256(b"other-data").hexdigest())

    def test_clear_removes_cached_entries(self):
        """Remove cached hashes when the cache is explicitly cleared."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "cache.sqlite3")
            file_path = os.path.join(temp_dir, "photo.jpg")
            with open(file_path, "wb") as media_file:
                media_file.write(b"photo-data")

            with HashCache(cache_path) as cache:
                cache.hash_file(file_path, os.stat(file_path))

            with HashCache(cache_path) as cache:
                self.assertEqual(cache.clear(), 1)
                self.assertIsNone(cache.get_hash(file_path, os.stat(file_path)))

    def test_manual_clean_command_clears_persistent_cache(self):
        """The manual command clears cached hashes from the configured database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "cache.sqlite3")
            file_path = os.path.join(temp_dir, "photo.jpg")
            with open(file_path, "wb") as media_file:
                media_file.write(b"photo-data")
            with HashCache(cache_path) as cache:
                cache.hash_file(file_path, os.stat(file_path))

            output = io.StringIO()
            with mock.patch.dict(os.environ, {"DEDUP_CACHE_PATH": cache_path}):
                with contextlib.redirect_stdout(output):
                    clean_cache()

            self.assertIn("... 1 cached file hash(es) removed !", output.getvalue())


if __name__ == "__main__":
    unittest.main()
