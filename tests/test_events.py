import unittest
from unittest import mock

import gazu.client
import gazu.events


class EventsInitTestCase(unittest.TestCase):
    def _make_client(self, verify, refresh_token):
        client = gazu.client.create_client("http://kitsu.example/api")
        client.session.verify = verify
        client.tokens = {
            "access_token": "acc",
            "refresh_token": refresh_token,
        }
        client.use_refresh_token = True
        return client

    @mock.patch("gazu.events.socketio.Client")
    def test_init_inherits_ssl_verify(self, Client):
        client = self._make_client(verify=False, refresh_token="ref")
        gazu.events.init(client=client)
        # ssl_verify is inherited from the client (False), not forced to True.
        # call_args[1] (kwargs) works on 3.7; .kwargs is 3.8+.
        self.assertFalse(Client.call_args[1]["ssl_verify"])

    @mock.patch("gazu.events.socketio.Client")
    def test_init_refreshes_token_on_reconnect_only(self, Client):
        event_client = Client.return_value
        client = self._make_client(verify=True, refresh_token="ref")
        with mock.patch.object(client, "refresh_access_token") as refresh:
            gazu.events.init(client=client)
            # connect receives a callable for the headers.
            _host, headers_cb = event_client.connect.call_args[0]
            self.assertTrue(callable(headers_cb))
            # First (initial) connect: current token, no refresh.
            self.assertEqual(headers_cb()["Authorization"], "Bearer acc")
            refresh.assert_not_called()
            # Subsequent (reconnect) attempts refresh the token.
            headers_cb()
            refresh.assert_called_once()


if __name__ == "__main__":
    unittest.main()
