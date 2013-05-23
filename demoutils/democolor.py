'''
Created on May 23, 2013

@author: sgallagh
'''

XTERM_DEFAULT = '0'
XTERM_BLACK = '30'
XTERM_RED = '31'
XTERM_GREEN = '32'
XTERM_YELLOW = '33'
XTERM_BLUE = '34'
XTERM_MAGENTA = '35'
XTERM_CYAN = '36'
XTERM_WHITE = '37'
XTERM_BOLD = '1'
XTERM_UNDER = '4'
XTERM_BLINK = '5'
XTERM_REVERSE = '7'

def hilite(string, color, bold=False):
    attr = []
    attr.append(color)
    if bold:
        attr.append(XTERM_BOLD)
    return u'\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
