
from deferred import Deferred

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

    def test_slowly(self):
        """
        
        """
        from browser import window
        d = Deferred()
        window.setTimeout(lambda: d.callback(None), 5000)
        return d
