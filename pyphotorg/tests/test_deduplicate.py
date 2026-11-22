import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

# Make the app's script modules importable when tests run from pyphotorg/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "work"))

from deduplicate import build_duplicate_df


class DeduplicateTests(unittest.TestCase):
    def test_hash_cache_preserves_duplicate_selection(self):
        """Reusing hashes preserves duplicate selection and skips unrelated sizes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            media_dir = os.path.join(temp_dir, "media")
            backup_dir = os.path.join(temp_dir, "backup")
            os.makedirs(media_dir)
            os.makedirs(backup_dir)
            for name in ("first.jpg", "second.jpg"):
                with open(os.path.join(media_dir, name), "wb") as media_file:
                    media_file.write(b"same-media")
            with open(os.path.join(media_dir, "unique.jpg"), "wb") as media_file:
                media_file.write(b"different-size")

            with mock.patch.dict(
                os.environ,
                {"DEDUP_CACHE_PATH": os.path.join(temp_dir, "cache.sqlite3")},
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    first_result = build_duplicate_df(
                        media_dir, backup_dir, dir_order_list=["/"]
                    )
                self.assertEqual(len(first_result), 2)
                self.assertEqual(int(first_result["duplicate"].sum()), 1)
                self.assertIn(
                    "... Hash cache: 0 hit(s), 2 file(s) hashed !",
                    output.getvalue(),
                )

                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    second_result = build_duplicate_df(
                        media_dir, backup_dir, dir_order_list=["/"]
                    )

                self.assertEqual(
                    second_result["duplicate"].tolist(),
                    first_result["duplicate"].tolist(),
                )
                self.assertIn(
                    "... Hash cache: 2 hit(s), 0 file(s) hashed !",
                    output.getvalue(),
                )


if __name__ == "__main__":
    unittest.main()
