import unittest
from unittest.mock import patch
import contents.exprvpnmon as source

class TestExpress(unittest.TestCase):


    def test_check_location(self):
        self.assertEquals(source.check_location('smart'), 'smart')
        self.assertEquals(source.check_location('usny'), 'usny')
        self.assertEquals(source.check_location('dub'), 'smart')
        self.assertEquals(source.check_location(), 'smart')

    def test_conn_status(self):
        with patch('exprvpnmon.subprocess.check_output') as mocked_output:
            mocked_output = b'Connected to New Jersey'
            self.assertEquals(source.conn_status(), True)

            mocked_output = b'Connected and A new version'
            self.assertEquals(source.conn_status(), True)

            mocked_output = b'Disconnected'
            self.assertEquals(source.conn_status(), False)

            mocked_output = b'Not found'
            self.assertEquals(source.conn_status(), False)


if __name__ == '__main__':
    unittest.main()