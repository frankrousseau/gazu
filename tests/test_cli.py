import os
import stat
import tempfile
import unittest
from unittest import mock

import gazu.cli


class CliConfigTestCase(unittest.TestCase):
    def test_save_config_writes_private_files(self):
        tmp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(tmp_dir, ".gazu")
        config_file = os.path.join(config_dir, "config.json")
        with mock.patch.object(
            gazu.cli, "CONFIG_DIR", config_dir
        ), mock.patch.object(gazu.cli, "CONFIG_FILE", config_file):
            gazu.cli.save_config({"host": "http://h/api", "tokens": {}})
            # File and directory must be owner-only (0600 / 0700).
            self.assertEqual(stat.S_IMODE(os.stat(config_file).st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(os.stat(config_dir).st_mode), 0o700)


if __name__ == "__main__":
    unittest.main()
