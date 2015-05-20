
from klein import run, route

from twisted.web.static import File
from twisted.internet.task import LoopingCall
from twisted.web.util import Redirect

BRYTHON_DIR = File("../Brython")

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
    for pkg in [File("../Deferred/deferred"),
                File("brytly")]:
        sitePackageDir.putChild(pkg.basename(), pkg)
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


run("localhost", 8912)
