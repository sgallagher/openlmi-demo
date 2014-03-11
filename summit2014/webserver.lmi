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

def main(argv):
    '''
    This script will install the 'httpd' package, configure
    it to start at boot and run the service immediately.
    '''

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

    print democolor.hilite("Communication established.",
                           democolor.XTERM_YELLOW)
    print democolor.hilite("Install %s package onto the system" % options.package,
                           democolor.XTERM_YELLOW)

    # Install the 'httpd' package
    packages = sw.find_package(ns, name=options.package)
    if not packages:
        stderr.write("Couldn't locate the %s package in the repository\n" % options.package)
        exit(5)
    package = packages.next()

    res = sw.install_package(ns, package)
    if not res:
        stderr.write(democolor.hilite("Could not install package\n",
                                      democolor.XTERM_RED))
        exit(2)

    print democolor.hilite("Installed %s package." % options.package,
                           democolor.XTERM_YELLOW)
    print democolor.hilite("Configure the %s service to autostart" % options.service,
                           democolor.XTERM_YELLOW)

    # Enable the service to start at boot
    try:
        service.enable_service(ns, options.service)
    except:
        stderr.write(democolor.hilite("Could not configure %s to start at boot\n" % options.service,
                                      democolor.XTERM_RED))
        exit(3)

    print democolor.hilite("Configured the %s service to auto-start." % options.service,
                           democolor.XTERM_YELLOW)
    print democolor.hilite("Start the %s service immediately." % options.service,
                           democolor.XTERM_YELLOW)

    # Start the webserver service
    try:
        service.start_service(ns, options.service)
    except:
        stderr.write(democolor.hilite("Could not start %s service\n" % options.service,
                                      democolor.XTERM_RED))
        exit(4)

        print democolor.hilite("The %s service started successfully." % options.service,
                           democolor.XTERM_YELLOW)

main(argv)
