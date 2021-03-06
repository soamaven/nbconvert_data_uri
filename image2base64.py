"""Citation handling for LaTeX output."""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, the IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from ipython_genutils.py3compat import PY3
if PY3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

__all__ = ['image2base64']


def image2base64(s):
    """Parse HTML image references in Markdown cells.

    This looks for HTML tags having a img tag name `img`
    and converts the image to a data URI for static embedding.
    The tranformation looks like this:

    `<img src="./Images/My_image.png" width="800" height="800" alt="Alt_name" title="Mytitle" align="center" />`

    Becomes

    `\\cite{granger}`

    Any HTML tag can be used, which allows the citations to be formatted
    in HTML in any manner.
    """
    parser = CitationParser()
    parser.feed(s)
    parser.close()
    outtext = u''
    startpos = 0
    for citation in parser.citelist:
            outtext += s[startpos:citation[1]]
            outtext += '\\cite{%s}'%citation[0]
            startpos = citation[2] if len(citation)==3 else -1
    outtext += s[startpos:] if startpos != -1 else ''
    return outtext

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------
class CitationParser(HTMLParser):
    """Citation Parser
    Replaces html tags with data-cite attribute with respective latex \\cite.

    Inherites from HTMLParser, overrides:
     - handle_starttag
     - handle_endtag
    """
    # number of open tags
    opentags = None
    # list of found citations
    citelist = None
    # active citation tag
    citetag = None

    def __init__(self):
        self.citelist = []
        self.opentags = 0
        HTMLParser.__init__(self)

    def get_offset(self):
        # Compute startposition in source
        lin, offset = self.getpos()
        pos = 0
        for i in range(lin-1):
            pos = self.data.find('\n',pos) + 1
        return pos + offset

    def handle_starttag(self, tag, attrs):
        # for each tag check if attributes are present and if no citation is active
        if self.opentags == 0 and len(attrs)>0:
            for atr, data in attrs:
                if atr.lower() == 'data-cite':
                    self.citetag = tag
                    self.opentags = 1
                    self.citelist.append([data, self.get_offset()])
                    return

        if tag == self.citetag:
            # found an open citation tag but not the starting one
            self.opentags += 1

    def handle_endtag(self, tag):
        if tag == self.citetag:
            # found citation tag check if starting one
            if self.opentags == 1:
                pos = self.get_offset()
                self.citelist[-1].append(pos+len(tag)+3)
            self.opentags -= 1

    def feed(self, data):
        self.data = data
        HTMLParser.feed(self, data)