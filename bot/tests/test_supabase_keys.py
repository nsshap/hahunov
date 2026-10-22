"""Constructor compatibility only: synthetic credentials, no network or data writes."""
import unittest
from unittest.mock import patch

import httpx
from supabase import create_client


class SupabaseKeyCompatibilityTests(unittest.TestCase):
    def test_supported_key_formats_reach_database_and_storage_clients_offline(self):
        keys = {
            "modern_secret": "sb_secret_SYNTHETIC_COMPATIBILITY_ONLY",
            "modern_publishable": "sb_publishable_SYNTHETIC_COMPATIBILITY_ONLY",
            "legacy_jwt": (
                "eyJhbGciOiJIUzI1NiJ9."
                "eyJyb2xlIjoic2VydmljZV9yb2xlIn0."
                "synthetic_signature_not_a_credential"
            ),
        }
        with patch.object(httpx.Client, "send", side_effect=AssertionError("network forbidden")) as sync_send:
            with patch.object(httpx.AsyncClient, "send", side_effect=AssertionError("network forbidden")) as async_send:
                for key_format, key in keys.items():
                    with self.subTest(key_format=key_format):
                        client = create_client("https://synthetic-ref.supabase.co", key)
                        self.assertEqual(client.supabase_key, key)
                        self.assertEqual(client.options.headers["apiKey"], key)
                        self.assertIsNotNone(client.table("congratulations"))
                        self.assertIsNotNone(client.storage.from_("congratulations"))
                sync_send.assert_not_called()
                async_send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
