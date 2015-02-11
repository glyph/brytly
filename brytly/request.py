"""
Treq-like module for issuing HTTP requests from the browser.
"""

from deferred import Deferred

from json import loads

from browser.ajax import ajax as Request

class Response(object):
    """
    An HTTP response.
    """
    # TODO: version
    version = ('HTTP', 1, 1)
    # TODO: content (raw bytes)
    # TODO: phrase
    # TODO: headers (and Headers class)
    # TODO: request attribute (and IClientRequest class)
    # TODO: previousResponse (is this even possible?)
    previousResponse = None
    # TODO: setPreviousResponse
    # TODO: deliverBody

    def __init__(self, req):
        """
        Create a L{Response} from a brython ajax L{Request}.
        """
        self._request = req
        self.code = getattr(req, "status", 0)
        self._contentDeferred = Deferred()
        def callContent(xmlHttpEvent):
            self._contentDeferred.callback(xmlHttpEvent.text)
        req.bind("complete", callContent)


    def text(self):
        """
        Get the text associated with this response.
        """
        return self._contentDeferred


    def json(self):
        """
        Get the JSON object associated with this response.
        """
        return self._contentDeferred.addCallback(loads)



def get(url, headers=None):
    """
    Fetch a URL and return a Deferred firing with a L{Response}.

    @param url: The URL to get.
    """
    result = Deferred()
    if headers is None:
        headers = {}

    req = Request()
    def fireIfNotFired(event):
        "Things have either started or completed; fire."
        if not result.called:
            result.callback(Response(req))
    # the "interactive" handler is where the deliverBody stuff would go
    req.bind("interactive", fireIfNotFired)
    def completeHandler(result):
        fireIfNotFired(result)
    req.bind("complete", completeHandler)
    req.open("GET", url, True)
    req.send()
    return result
