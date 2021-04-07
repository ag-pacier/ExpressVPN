import unittest
from unittest.mock import patch
import contents.exprvpnmon

class TestExpress(unittest.TestCase):


    def test_check_location(self):
        self.assertEquals(contents.exprvpnmon.check_location('smart'), 'smart')
        self.assertEquals(contents.exprvpnmon.check_location('usny'), 'usny')
        self.assertEquals(contents.exprvpnmon.check_location('dub'), 'smart')

    def test_conn_status(self):
        with patch('contents.exprvpnmon.subprocess.check_output') as mocked_output:
            mocked_output = b'Connected to New Jersey'
            self.assertEquals(contents.exprvpnmon.conn_status(), True)

            mocked_output = b'Connected and A new version'
            self.assertEquals(contents.exprvpnmon.conn_status(), True)

            mocked_output = b'Disconnected'
            self.assertEquals(contents.exprvpnmon.conn_status(), False)

            mocked_output = b'Not found'
            self.assertEquals(contents.exprvpnmon.conn_status(), False)


if __name__ == '__main__':
    unittest.main()