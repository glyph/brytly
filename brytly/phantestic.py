
from deferred import maybeDeferred, Deferred, Failure

class TestFailure(Exception):
    """
    A test failed.
    """


class SuiteRun(object):
    counter = 0
    def __init__(self, suiteID, caseIterator, result):
        SuiteRun.counter += 1
        self.instanceNumber = SuiteRun.counter
        self.suiteID = suiteID
        self.caseIterator = caseIterator
        self.result = result
        self.finished = Deferred()


    def keepGoing(self):
        try:
            case = next(self.caseIterator)
        except StopIteration:
            self.finished.callback(self)
        else:
            d = case.run(self.result)
            d.addBoth(lambda result: self.keepGoing())


    def __str__(self):
        """
        Repr for SuiteRun.
        """
        return "<SuiteRun for " + self.suiteID + ">"



class TestSuite(object):
    def __init__(self, id, cases):
        self.cases = cases
        self._id = id


    def id(self):
        return self._id


    def run(self, result):
        run = SuiteRun(self.id(), iter(self.cases), result)
        run.keepGoing()
        return run.finished



class TestCase(object):
    def __init__(self, methodName):
        self.methodName = methodName


    def successResultOf(self, d):
        """
        Get the result of Deferred.
        """
        l = []
        def appendit(x):
            l.append(x)
            return x
        d.addBoth(appendit)
        self.assertEquals(len(l), 1, "No result found.")
        if isinstance(l[0], Failure):
            l[0].printTraceback()
            l[0].raiseException()
        return l[0]


    def assertNoResult(self, d):
        """
        Assert that a Deferred has no result.
        """
        l = []
        def appendit(x):
            l.append(x)
            return x
        d.addBoth(appendit)
        if len(l) != 0:
            self.assertEquals(0, 1,
                              "Expected no result, but found " + repr(l[0]))


    def id(self):
        return (self.__class__.__module__ + '.' + self.__class__.__name__ +
                '.' + self.methodName)


    def assertEquals(self, a, b, failMessage=None):
        if a != b:
            if failMessage is None:
                failMessage = repr(a) + " != " + repr(b)
            raise TestFailure(failMessage)


    @classmethod
    def suite(cls):
        cases = []
        for method in dir(cls):
            if method.startswith("test"):
                cases.append(cls(method))
        return TestSuite(cls.__module__ + '.' + cls.__name__, cases)


    def run(self, result):
        self.result = result
        result.started(self)
        d = maybeDeferred(getattr(self, self.methodName))
        def ok(r):
            result.success(self)
            return "TEST/OK"
        def bad(r):
            result.failure(self, r.getTraceback())
            return "TEST/FAIL"
        d.addCallbacks(ok, bad)
        return d



class PhantomResult(object):

    def __init__(self, callPhantom):
        self.passes = 0
        self.failures = 0
        self.callPhantom = callPhantom


    def started(self, case):
        caseID = case.id()
        self.callPhantom({'command': 'test-started',
                          'caseID': caseID})


    def success(self, case):
        caseID = case.id()
        self.passes += 1
        self.callPhantom({'command': 'test-ended',
                          'caseID': caseID,
                          'failed': False});


    def failure(self, case, explanation):
        caseID = case.id()
        self.failures += 1
        self.callPhantom({'command': 'test-ended',
                          'caseID': caseID,
                          'failed': True,
                          'explanation': explanation})


    def done(self):
        failed = int(self.failures != 0)
        if failed:
            result = 'FAILED'
        else:
            result = 'OK'
        print("Results: [%s] %d PASSED %d FAILED" %
              (result, self.passes, self.failures))
        self.callPhantom({'command': 'run-ended', 'status': failed})



class Executor(object):

    def __init__(self, namespace):
        cases = []
        skip = ['__class__', '__repr__']
        for key in namespace:
            if key in skip:
                continue
            obj = namespace[key]
            t = type(obj)
            if t is type:
                if issubclass(obj, TestCase):
                    if obj is not TestCase:
                        cases.append(namespace[key].suite())
        self.suite = TestSuite("Root", cases)


    def execute(self):
        from browser import window
        if hasattr(window, "callPhantom"):
            callPhantom = window.callPhantom
        else:
            callPhantom = window.console.log
        result = PhantomResult(callPhantom)
        def done(what):
            result.done()
        self.suite.run(result).addBoth(done)

