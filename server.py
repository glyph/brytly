
from klein import route

from twisted.python.filepath import FilePath
from twisted.web.static import File
from twisted.internet.task import LoopingCall
from twisted.web.util import Redirect

from twisted.python.modules import theSystemPath

BRYTHON_DIR = File(FilePath(__file__).sibling("Brython").path)

@route("/slow")
def slow(request):
    """
    Return some bytes, slowly.
    """
    request.setHeader("content-length", "100")
    def deliver():
        if deliver.count == 100:
            lc.stop()
        else:
            request.write(b"x")
            deliver.count += 1
    deliver.count = 0
    lc = LoopingCall(deliver)
    return lc.start(0.01).addCallback(lambda anything: b"")



@route("/")
def slash(request):
    """
    Redirect to /www for now.
    """
    return Redirect("/www")



@route("/www/src/Lib/site-packages/", branch=True, strict_slashes=True)
def sitePackages(request):
    """
    This is a bit of a hack until there is some official way to do
    https://github.com/brython-dev/brython/issues/119
    """
    sitePackageDir = (BRYTHON_DIR
                      .getChild("www", request)
                      .getChild("src", request)
                      .getChild("Lib", request)
                      .getChild("site-packages", request))
    def pathEntryFiles():
        # Special case Deferred since there's no brython-compatible version on
        # PyPI yet.
        yield File(
            FilePath(__file__).sibling("Deferred").child("deferred").path
        )
        for pkg in theSystemPath.iterModules():
            if pkg.isPackage():
                pkgdir = pkg.filePath.parent()
                # print("ADDING", pkgdir.basename())
                modulePackage = File(pkgdir.path)
                yield modulePackage
    for pathEntryFile in pathEntryFiles():
        sitePackageDir.putChild(pathEntryFile.basename(), pathEntryFile)
    return sitePackageDir



@route("/www/", branch=True, strict_slashes=True)
def site(request):
    """
    Get the /www/ dir from brython.
    """
    return BRYTHON_DIR.getChild("www", request)



@route("/test")
def test(request):
    """
    Test cases.
    """
    return """<!DOCTYPE html>
        <html>
          <head>
            <title>TESTS</title>
            <script src="/www/src/brython.js"></script>
          </head>
          <body onload="brython()">
            L O A D I N G
            <script type="text/python">
              from browser import window
              def begin():
                from brytly.phantestic import Executor
                from brytly.test import test_stub
                window.document.body.html = 'O K A Y'
                e = Executor(test_stub.__dict__)
                e.execute()
              window.setTimeout(begin, 200)
            </script>
          </body>
        </html>
    """


@route("/ajax")
def ajax(request):
    """
    A page with some AJAX.
    """
    return open("ajax.html").read()



if __name__ == '__main__':
    from twisted.web.server import Site
    from twisted.web.resource import IResource
    from twisted.internet import reactor
    from twisted.internet.endpoints import serverFromString
    from twisted.python.components import proxyForInterface
    from twisted.logger import globalLogBeginner, textFileLogObserver

    def fixpp(request):
        while True:
            try:
                idx = request.postpath.index(b'')
            except ValueError:
                break
            else:
                if idx + 1 == len(request.postpath):
                    break
                else:
                    request.postpath.pop(idx)

    class Deslasher(proxyForInterface(IResource)):
        def render(self, request):
            """
            Klein's resource is a leaf, so everything goes through render() and
            does dispatch internally.
            """
            fixpp(request)
            return super(Deslasher, self).render(request)

    from klein import resource
    root = Deslasher(resource())

    endpoint = serverFromString(reactor, b"tcp:8192")
    endpoint.listen(Site(root))
    import sys
    globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])

    reactor.run()
