
from brytly.phantestic import TestCase

class MyTest(TestCase):
    """
    A test case.
    """

    def test_ok(self):
        """
        
        """
        self.assertEquals(1, 1)

    def test_fail(self):
        """
        
        """
        self.assertEquals(1, 0)
