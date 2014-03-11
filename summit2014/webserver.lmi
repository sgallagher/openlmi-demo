#! /usr/bin/lmishell

from sys import argv, stdout, stderr, exit
from os import getuid
from getpass import getpass

import lmi.scripts.software as sw
import lmi.scripts.service as service

from lmi.shell import connect
from lmidemo.util import establish_connection, init_parser
import lmidemo.util.democolor as democolor

# Add custom arguments for this demo
def add_args(parser):
    parser.add_argument('--package',
                        dest='package',
                        action='store',
                        help='The software package to install on the managed system',
                        default='httpd')
    parser.add_argument('--service',
                        dest='service',
                        action='store',
                        help='The system service to enable and launch on the managed system',
                        default='httpd')
    return parser

def keypress(text):
    # Add pause for demo operator. Press enter to continue.
    raw_input(text)

def main(argv):
    '''
    This script will install the 'httpd' package, configure
    it to start at boot and run the service immediately.
    '''

    print democolor.hilite(main.__doc__, democolor.XTERM_BOLD)

    parser = init_parser('Install a service on the target '
                         'system, enable it to start by default, '
                         'and then start the service.')
    parser = add_args(parser)

    options = parser.parse_args()

    print democolor.hilite("Establish OpenLMI communication to managed system.",
                           democolor.XTERM_YELLOW)

    # Connect to the remote (or local) OpenLMI managed system
    c = establish_connection(options)
    ns = c.root.cimv2

    keypress(democolor.hilite("Communication established.",
                              democolor.XTERM_WHITE))

    # Use keypress to pause for demo operator to finish talking.
    keypress(democolor.hilite("Install %s package onto the system using the OpenLMI Software Provider" % options.package,
                              democolor.XTERM_YELLOW))

    # Install the 'httpd' package
    packages = sw.find_package(ns, name=options.package)
    if not packages:
        stderr.write("Couldn't locate the %s package in the repository\n" % options.package)
        exit(5)
    package = packages.next()

    try:
        res = sw.install_package(ns, package)
        if not res:
            stderr.write(democolor.hilite("Could not install package\n",
                                          democolor.XTERM_RED))
            exit(2)
        keypress(democolor.hilite("Installed %s package." % options.package,
                                  democolor.XTERM_WHITE))
    except Exception as detail:
        stderr.write(democolor.hilite("Could not install package\n%s\n" % detail,
                                      democolor.XTERM_RED))

    keypress(democolor.hilite("Configure the %s service to autostart using the OpenLMI Services Provider" % options.service,
                              democolor.XTERM_YELLOW))

    # Enable the service to start at boot
    try:
        service.enable_service(ns, options.service)
    except:
        stderr.write(democolor.hilite("Could not configure %s to start at boot\n" % options.service,
                                      democolor.XTERM_RED))
        exit(3)

    keypress(democolor.hilite("%s will now start automatically at boot." % options.service,
                              democolor.XTERM_WHITE))

    keypress(democolor.hilite("Start the %s service immediately using the OpenLMI Services Provider." % options.service,
                              democolor.XTERM_YELLOW))

    # Start the webserver service
    try:
        service.start_service(ns, options.service)
    except:
        stderr.write(democolor.hilite("Could not start %s service\n" % options.service,
                                      democolor.XTERM_RED))
        exit(4)

    print democolor.hilite("The %s service started successfully." % options.service,
                       democolor.XTERM_WHITE)

main(argv)
