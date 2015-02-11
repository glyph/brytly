
from browser import document
from browser.html import P
from brytly.request import get

def bprint(arg):
    """
    Print a thing into the document.
    """
    document <= P(arg)

def go_slow(ev):
    """
    do some stuff
    """
    slow = get("/slow")
    @slow.addCallback
    def show(result):
        bprint(repr(result))
        return result.text()

    @slow.addCallback
    def showContent(result):
        bprint(repr(result))
    return True
