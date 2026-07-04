import unittest

import requests_mock

import gazu.client
from zou_route_gate import is_known_route, request_path


class ZouRouteGateTestCase(unittest.TestCase):
    def test_accepts_a_real_route(self):
        self.assertTrue(is_known_route("/data/tasks/open-tasks"))
        self.assertTrue(is_known_route("/data/projects/anything/sequences"))

    def test_rejects_an_invented_route(self):
        # Invented routes that don't collide with the generic CRUD
        # <model>/<id> shape (the bulk of the Dec 2025 bad batch).
        self.assertFalse(is_known_route("/data/user/avatar"))
        self.assertFalse(
            is_known_route("/pictures/preview-files/x/extract-tile")
        )
        self.assertFalse(is_known_route("/data/comments/x/preview-files"))

    def test_crud_shape_collision_is_a_known_gap(self):
        # "/data/tasks/open" matches the CRUD "/data/tasks/<task_id>" shape,
        # so the gate cannot distinguish it from a real get-by-id. Documented
        # limitation (test ids aren't UUIDs, so we can't tighten the match).
        self.assertTrue(is_known_route("/data/tasks/open"))

    def test_request_path_strips_api_prefix(self):
        url = gazu.client.get_full_url("data/tasks/open-tasks")
        self.assertEqual(request_path(url), "/data/tasks/open-tasks")

    def test_external_urls_are_skipped(self):
        self.assertIsNone(request_path("https://example.com/some/file.png"))

    def test_gate_rejects_registering_an_invented_route(self):
        # Proves the autouse gate actually raises (not silently passing):
        # registering a mock for an invented route must fail.
        with self.assertRaises(AssertionError):
            with requests_mock.mock() as mock:
                mock.delete(
                    gazu.client.get_full_url("data/user/avatar"), text=""
                )


if __name__ == "__main__":
    unittest.main()
