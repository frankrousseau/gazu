import contextlib
import io
import json
import os
import stat
import tempfile
import unittest
from unittest import mock

import pytest

pytest.importorskip("click")  # cli extra is optional; skip if absent

import requests_mock
from click.testing import CliRunner

import gazu.cli
import gazu.client

from utils import fakeid


class CliTasksTestCase(unittest.TestCase):
    def test_tasks_status_only_filters_by_status(self):
        # Passing only --status must filter, not silently return all tasks.
        host = gazu.client.get_host()
        proj_id = fakeid("project-1")
        wip_id = fakeid("status-wip")
        config = {"host": host, "tokens": {"access_token": "x"}}
        with mock.patch.object(gazu.cli, "load_config", return_value=config):
            with requests_mock.mock() as m:
                m.get(
                    gazu.client.get_full_url(f"data/projects/{proj_id}"),
                    json={"id": proj_id, "name": "P"},
                )
                m.get(
                    gazu.client.get_full_url("data/task-status"),
                    json=[{"id": wip_id, "short_name": "wip"}],
                )
                m.get(
                    gazu.client.get_full_url("data/tasks"),
                    json=[
                        {"id": "t1", "task_status_id": wip_id},
                        {"id": "t2", "task_status_id": fakeid("other")},
                    ],
                )
                result = CliRunner().invoke(
                    gazu.cli.cli,
                    ["--json", "tasks", "-p", proj_id, "-s", "wip"],
                )
        self.assertEqual(result.exit_code, 0, result.output)
        ids = [task["id"] for task in json.loads(result.output)]
        self.assertEqual(ids, ["t1"])


class CliPrintTableTestCase(unittest.TestCase):
    def test_print_table_keeps_falsy_values(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gazu.cli.print_table(
                [{"name": "Shot 1", "frames": 0}],
                [("NAME", "name"), ("FRAMES", "frames")],
            )
        # 0 must render as "0", not a blank cell.
        self.assertIn("0", buf.getvalue().splitlines()[-1])


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
