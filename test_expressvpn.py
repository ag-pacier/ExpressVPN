import unittest
from unittest import mock
from unittest.mock import patch
import contents.exprvpnmon

class TestExpress(unittest.TestCase):


    def test_check_location(self):
        self.assertEqual(contents.exprvpnmon.check_location('smart'), 'smart')
        self.assertEqual(contents.exprvpnmon.check_location('usny'), 'usny')
        self.assertEqual(contents.exprvpnmon.check_location('dub'), 'smart')

    def test_conn_status(self):
        with patch('contents.exprvpnmon.subprocess.check_output') as mocked_output:
            mocked_output.return_value = b'Connected to New Jersey'
            self.assertEqual(contents.exprvpnmon.conn_status(), True)

            mocked_output.return_value = b'Connected\nA new version'
            self.assertEqual(contents.exprvpnmon.conn_status(), True)

            mocked_output.return_value = b'Disconnected'
            self.assertEqual(contents.exprvpnmon.conn_status(), False)

            mocked_output.return_value = b'Not found'
            self.assertEqual(contents.exprvpnmon.conn_status(), False)


if __name__ == '__main__':
    unittest.main()