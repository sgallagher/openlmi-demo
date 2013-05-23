# !/usr/bin/env lmishell

'''
Created on Apr 8, 2013

@author: sgallagh
'''

import sys
import time

# Machine to contact
server = "openlmi-demo.example.com"
username = "root"
password = "redhat"

# Connect to the example VM
print "Connecting to remote server \"{0}\"".format(server)
c = connect(server, username, password)

# Shorthand the cimv2 namespace
ns = c.root.cimv2

# Display all services configured to start by default and their current status
print "== Services configured to start at boot =="
for service in ns.LMI_Service.instances():
    if service.EnabledDefault == 2:  # 2 means enabled, 3 means disabled
        print service.Name + ": " \
              + ("1" if service.Started else "0") \
              + " (" + service.Status + ")"

time.sleep(3)

print "== Restarting auditd via OpenLMI =="
auditd = ns.LMI_Service.first_instance(key="Name", value="auditd")
print "auditd status: ({0})".format(auditd.Status)
time.sleep(3)

print "Stopping auditd..."
auditd.StopService()
time.sleep(3)

print "auditd status: ({0})".format(auditd.Status)
print "Starting auditd..."
auditd.StartService()
time.sleep(3)

print "auditd status: ({0})".format(auditd.Status)
