# !/usr/bin/env lmishell

'''
Created on Apr 8, 2013

@author: sgallagh
'''

import sys
import time
import demoutils.democolor as democolor

def display_service_status(service):
    sys.stdout.write("{0} status: ".format(service.Name))
    print democolor.hilite(service.Status, democolor.XTERM_CYAN \
                 if service.Started else democolor.XTERM_RED)

# Machine to contact
server = "openlmi-demo.example.com"
username = "root"
password = "redhat"

# Connect to the example VM
print democolor.hilite("\nConnecting to remote server \"{0}\"".format(server),
             democolor.XTERM_WHITE)
c = connect(server, username, password)

# Shorthand the cimv2 namespace
ns = c.root.cimv2

# Display all services configured to start by default and their current status
print democolor.hilite("== Interrogating services configured to start at boot "
                       "Using OpenLMI ==",
             democolor.XTERM_MAGENTA, True)
for service in ns.LMI_Service.instances():
    if service.EnabledDefault == 2:  # 2 means enabled, 3 means disabled
        display_service_status(service)
        time.sleep(1)

time.sleep(2)

print democolor.hilite("\n== Restarting auditd via OpenLMI ==",
             democolor.XTERM_MAGENTA, True)
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
