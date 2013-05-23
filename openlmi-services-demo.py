# !/usr/bin/env lmishell

'''
Created on Apr 8, 2013

@author: sgallagh
'''

import sys
import time

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
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def display_service_status(service):
    sys.stdout.write("{0} status: ".format(service.Name))
    print hilite(service.Status, XTERM_CYAN if service.Started else XTERM_RED)

# Machine to contact
server = "openlmi-demo.example.com"
username = "root"
password = "redhat"

# Connect to the example VM
print hilite("\nConnecting to remote server \"{0}\"".format(server),
             XTERM_WHITE)
c = connect(server, username, password)

# Shorthand the cimv2 namespace
ns = c.root.cimv2

# Display all services configured to start by default and their current status
print hilite("== Services configured to start at boot ==", XTERM_MAGENTA, True)
for service in ns.LMI_Service.instances():
    if service.EnabledDefault == 2:  # 2 means enabled, 3 means disabled
        display_service_status(service)
        time.sleep(1)

time.sleep(2)

print hilite("\n== Restarting auditd via OpenLMI ==", XTERM_MAGENTA, True)
auditd = ns.LMI_Service.first_instance(key="Name", value="auditd")
display_service_status(auditd)
time.sleep(3)

print "Stopping auditd..."
auditd.StopService()
time.sleep(3)

display_service_status(auditd)
print "Starting auditd..."
auditd.StartService()
time.sleep(3)

display_service_status(auditd)
