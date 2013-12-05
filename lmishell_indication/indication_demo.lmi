import sys
import time
import pynotify
import os
import getpass

listening_port = 65500

def useradd_notifier(indication, **kwargs):
    '''
    Asynchronous notification routine that will trigger when the listener
    receives a CIM indication that a user has been added to the system.
    '''

    # Write a message to standard output (the terminal)
    sys.stdout.write("new user added\n")

    # Also send a notification to the notification message bus on the user's
    # desktop display.
    n = pynotify.Notification("New user", "A new user was added to the system")

    if not n.show():
        sys.stderr.write("Failed to send notification")
        sys.exit(5)

def establish_connection():
    '''
    Prompt for the hostname to contact and the username and password, if
    necessary.
    '''

    # Prompt for the hostname
    hostname = raw_input('Hostname: ')
    host_uri = "https://%s" % hostname

    # Run this script as root and this will use the
    # local UNIX socket. Otherwise, modify this line
    # to match the system you are connecting to

    if os.getuid() == 0 and hostname == 'localhost':
        c = connect(hostname)
    else:
        # Prompt for user and password
        user = raw_input('User: ')
        passwd = getpass.getpass("Password: ")

        c = connect(host_uri, user, passwd)

    if not c:
        sys.stderr.write("Couldn't authenticate\n")
        sys.exit(1)
    return c

def create_listener(port):
    '''
    Creates a listener thread to wait for the add-user indication
    '''

    # First, start up an indication listener
    listener = LMIIndicationListener("0.0.0.0", port)

    # Create a URI for listeners to submit to the indication enrollment
    listener_uri = "http://localhost:%d" % (port)

    # We pass an indication name with XXXXXXXX in it, which will be internally
    # replaced with a unique identifier, to ensure that this name doesn't
    # conflict with any other client to the system (and so multiple copies of
    # this demo can be run safely at the same time.
    uniquename = listener.add_handler("useradd-XXXXXXXX", useradd_notifier)

    sys.stdout.write("useradd handler created, starting listener for %s\n" % uniquename)


    # Start listening for the user-add indications.
    # This method will start a new thread and an HTTP listener in that thread.
    # It will be terminated automatically when the application exits, but we
    # could shut it down sooner with listener.stop() as well.
    res = listener.start()
    if not res:
        sys.stderr.write("I'm a poor listener\n")
        sys.exit(2)

    return listener, listener_uri, uniquename

def subscribe_adduser(c, uniquename, listener_uri):
    '''
    This routine creates a new indication subscription on the CIMOM, telling
    the CIMOM to send an indication to the Destination address when a user is
    added to the system.
    '''

    # Subscribe to the account creation indication
    retval = c.subscribe_indication(
        # The unique name of this indication, to differentiate it from other
        # clients of the managed system.
        Name=uniquename,

        # A CQL query that will return the indication object for which we
        # want to register.
        # TODO: link to CQL reference
        Query='SELECT * FROM LMI_AccountInstanceCreationIndication WHERE SOURCEINSTANCE ISA LMI_Account',

        # This is the destination computer, where all the indications will be
        # delivered
        Destination=listener_uri,

        # The following attributes are standardized and should not be changed.
        # As of today, the upstream master repository makes these attributes
        # optional, but as of the time of this writing, it is not part of the
        # any released version, so we need to include them.
        FilterCreationClassName="CIM_IndicationFilter",
        FilterSystemCreationClassName="CIM_ComputerSystem",
        FilterSourceNamespace="root/cimv2",
        QueryLanguage="DMTF:CQL",
        CreationNamespace="root/interop",
        SubscriptionCreationClassName="CIM_IndicationSubscription",
        HandlerCreationClassName="CIM_IndicationHandlerCIMXML",
        HandlerSystemCreationClassName="CIM_ComputerSystem"
    )

    if not retval or not retval.rval:
        sys.stderr.write("Failed to register indication: %s\n" % retval.errorstr)
        sys.exit(2)


def main():
    '''
    This script creates a new indication listener and registers it with the
    OpenLMI CIMOM. It will print a message both on the terminal and via
    desktop notifications when a user is added to the managed system.
    '''

    sys.stdout.write("== Testing Indication Support in LMIShell ==\n")
    sys.stdout.write("This example will start up an indication listener for\n")
    sys.stdout.write("the creation of a new user on the system and will print\n")
    sys.stdout.write("a message to the console as well as issuing a\n")
    sys.stdout.write("notification on the libnotify bus.\n")

    # Initialize the desktop message bus
    if not pynotify.init("lmishell_indication"):
        sys.stderr.write('Could not initialize notification bus\n')
        sys.exit(4)

    # Connect to the remote (or local) OpenLMI managed system
    c = establish_connection()

    sys.stdout.write("Starting up indication listener\n")

    # First, start up an indication listener

    listener, listener_uri, uniquename = create_listener(listening_port)
    sys.stdout.write("listener started, subscribing to indication\n")

    # Subscribe to the account creation indication
    subscribe_adduser(c, uniquename, listener_uri)

    sys.stdout.write('indication registered\n')

    # Loop forever. The listener is running in another thread.
    while True:
        time.sleep(90)
        pass

    # When the is interrupted (such as by SIGTERM aka ctrl-c), the process will
    # return control to the lmishell, which will automatically unsubscribe all
    # indications associated with this script.

main()
