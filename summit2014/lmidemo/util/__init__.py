from sys import argv, stdout, stderr, exit
import argparse
from os import getuid
from getpass import getpass

from lmi.shell import connect
import democolor as democolor

def establish_connection(options):
    '''
    Prompt for the hostname to contact and the username and password, if
    necessary.
    '''

    if not options.hostname:
        # Prompt for the hostname
        hostname = raw_input('Hostname: ')
    else:
        hostname = options.hostname

    host_uri = "https://%s" % hostname

    # Run this script as root and this will use the
    # local UNIX socket. Otherwise, modify this line
    # to match the system you are connecting to

    if getuid() == 0 and hostname == 'localhost':
        print(democolor.hilite("lmi.shell.LMIConnection.connect('%s')" % hostname))
        c = connect(hostname)
    else:
        # Prompt for user and password
        if not options.username:
            user = raw_input('User: ')
        else:
            user = options.username

        if not options.password:
            passwd = getpass("Password: ")
        else:
            passwd = options.password

        print(democolor.hilite("lmi.shell.LMIConnection.connect('%s', '%s', '%s')" % (
                                   hostname, user, passwd),
                               democolor.XTERM_MAGENTA))
        c = connect(host_uri, user, passwd,
                    verify_server_cert=options.verify)

    if not c:
        stderr.write(democolor.hilite("Couldn't authenticate\n",
                                      democolor.XTERM_RED))
        exit(1)
    return c

# Parse common command-line arguments
def init_parser(desc):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-n', '--noverify',
                        dest='verify',
                        action='store_false',
                        help='Implicitly trust SSL certificates',
                        default=True)
    parser.add_argument('--host',
                        dest='hostname',
                        action='store',
                        help='The hostname or IP address of the managed system',
                        default=None)
    parser.add_argument('-u', '--user',
                        dest='username',
                        action='store',
                        help='The username for the OpenLMI connection',
                        default=None)
    parser.add_argument('-p', '--password',
                        dest='password',
                        help='The password for the OpenLMI connection',
                        action='store',
                        default=None)
    return parser
