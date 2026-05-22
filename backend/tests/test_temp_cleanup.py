from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.main import _cleanup_temp_dir_once  # noqa: E402
from src.repositories.artifacts import get_artifact, register_artifact  # noqa: E402
from src.repositories.storage import configure_database_path, init_storage  # noqa: E402


class TempCleanupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir_context.name)
        configure_database_path(self.root / 'appslides.db')
        init_storage(self.root / 'appslides.db')

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def test_cleanup_removes_expired_temp_entries_and_artifact_rows(self) -> None:
        temp_root = self.root / 'runtime' / 'temp'
        old_dir = temp_root / 'conversions' / 'old-job'
        old_dir.mkdir(parents=True)
        old_file_in_dir = old_dir / 'result.pdf'
        old_file_in_dir.write_bytes(b'old')

        old_standalone_file = temp_root / 'presentations' / 'old.tmp'
        old_standalone_file.parent.mkdir(parents=True)
        old_standalone_file.write_bytes(b'old')

        fresh_dir = temp_root / 'uploads' / 'fresh-job'
        fresh_dir.mkdir(parents=True)
        fresh_file = fresh_dir / 'source.pptx'
        fresh_file.write_bytes(b'fresh')

        old_artifact = register_artifact(old_file_in_dir, kind='pdf', media_type='application/pdf')
        old_file_artifact = register_artifact(old_standalone_file, kind='other', media_type='application/octet-stream')
        fresh_artifact = register_artifact(
            fresh_file,
            kind='pptx',
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        )

        old_timestamp = time.time() - 7200
        for path in (old_file_in_dir, old_dir, old_standalone_file):
            os.utime(path, (old_timestamp, old_timestamp))

        removed_dirs, removed_files, removed_artifacts = _cleanup_temp_dir_once(temp_root, ttl_seconds=3600)

        self.assertEqual(removed_dirs, 1)
        self.assertEqual(removed_files, 1)
        self.assertEqual(removed_artifacts, 2)
        self.assertFalse(old_dir.exists())
        self.assertFalse(old_standalone_file.exists())
        self.assertTrue(fresh_file.exists())
        self.assertIsNone(get_artifact(old_artifact.artifact_id))
        self.assertIsNone(get_artifact(old_file_artifact.artifact_id))
        self.assertIsNotNone(get_artifact(fresh_artifact.artifact_id))


if __name__ == '__main__':
    unittest.main()
