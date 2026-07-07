from django.test import SimpleTestCase

from accounts.models import generate_mtb_uuid


class GenerateMtbUuidTests(SimpleTestCase):
    def test_generate_mtb_uuid_returns_expected_prefix(self):
        value = generate_mtb_uuid()

        self.assertTrue(value.startswith("MTB"))
        self.assertEqual(len(value), 13)
