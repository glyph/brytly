
from brytly.phantestic import TestCase

class MyTest(TestCase):
    """
    A test case.
    """

    def test_ok(self):
        """
        
        """
        print("ok")

    def test_fail(self):
        """
        
        """
        print("fail")
        self.assertEquals(1, 0)
