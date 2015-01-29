
from deferred import maybeDeferred, Deferred, Failure



class TestFailure(Exception):
    """
    A test failed.
    """



class SuiteRun(object):
    def __init__(self, caseIterator, result):
        self.caseIterator = caseIterator
        self.result = result
        self.finished = Deferred()


    def keepGoing(self):
        try:
            case = self.caseIterator.next()
        except StopIteration:
            self.finished.callback(None)
        else:
            case.run(self.result).addBoth(lambda result: self.keepGoing())



class TestSuite(object):
    def __init__(self, id, cases):
        self.cases = cases
        self._id = id


    def id(self):
        return self._id


    def run(self, result):
        run = SuiteRun(iter(self.cases), result)
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
        def bad(r):
            result.failure(self, r.getTraceback())
        d.addCallbacks(ok, bad)
        return d



class PhantomResult(object):

    def __init__(self):
        self.passes = 0
        self.failures = 0
        JS("""
        if ($wnd.callPhantom === undefined) {
            $wnd.callPhantom = function (x) {
                console.log(x);
            }
        }
        """)


    def started(self, case):
        caseID = case.id()
        caseID
        JS("""
            $wnd.callPhantom({'command': 'test-started',
                        'caseID': caseID});
        """)


    def success(self, case):
        caseID = case.id()
        caseID
        self.passes += 1
        JS("""
            $wnd.callPhantom({'command': 'test-ended',
                        'caseID': caseID,
                        'failed': false});
        """)


    def failure(self, case, explanation):
        caseID = case.id()
        caseID
        self.failures += 1
        JS("""
            $wnd.callPhantom({'command': 'test-ended',
                        'caseID': caseID,
                        'failed': true,
                        'explanation': explanation});
        """)


    def done(self):
        failed = int(self.failures != 0)
        if failed:
            result = 'FAILED'
        else:
            result = 'OK'
        print("Results: [%s] %d PASSED %d FAILED" %
              (result, self.passes, self.failures))
        JS("""
            $wnd.callPhantom({'command': 'exit', 'status': @{{failed}}});
        """)



def type_workaround(x):
    try:
        return type(x)
    except:
        class Dummy:
            pass
        return Dummy



class Executor(object):

    def __init__(self, namespace):
        cases = []
        skip = ['__was_initialized__', '__repr__']
        for key in namespace:
            if key in skip:
                continue
            obj = namespace[key]
            t = type_workaround(obj)
            if t is type and issubclass(obj, TestCase) and obj is not TestCase:
                cases.append(namespace[key].suite())
        self.suite = TestSuite("Root", cases)


    def execute(self):
        result = PhantomResult()
        def done(what):
            result.done()
        self.suite.run(result).addBoth(done)

# discover test cases
# execute test cases
