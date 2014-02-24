from sys import argv, stdout, stderr, exit
from os import getuid
from getpass import getpass

from lmi.shell import connect

def establish_connection(hostname):
    '''
    Prompt for the hostname to contact and the username and password, if
    necessary.
    '''

    if not hostname:
        # Prompt for the hostname
        hostname = raw_input('Hostname: ')

    host_uri = "https://%s" % hostname

    # Run this script as root and this will use the
    # local UNIX socket. Otherwise, modify this line
    # to match the system you are connecting to

    if getuid() == 0 and hostname == 'localhost':
        c = connect(hostname)
    else:
        # Prompt for user and password
        user = raw_input('User: ')
        passwd = getpass("Password: ")

        c = connect(host_uri, user, passwd)

    if not c:
        stderr.write("Couldn't authenticate\n")
        exit(1)
    return c