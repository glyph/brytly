
from deferred import Deferred

from brytly.phantestic import TestCase

class MyTest(TestCase):
    """
    A test case.
    """

    def test_ok(self):
        """
        This test should pass.
        """
        self.assertEquals(1, 1)

    def test_fail(self):
        """
        This test should fail.
        """
        self.assertEquals(1, 0)

    def test_slowly(self):
        """
        This test should wait for 5 seconds for its Deferred to fire, then
        pass.
        """
        from browser import window
        d = Deferred()
        print("one")
        later = lambda: d.callback(None)
        print("two")
        window.setTimeout(later, 5000)
        print("three")
        return d
