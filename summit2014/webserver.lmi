from sys import argv, stdout, stderr, exit
from os import getuid
from getpass import getpass

import lmi.scripts.software as sw
import lmi.scripts.service as service

from lmidemo.util import establish_connection

def main(argv):
    '''
    This script will install the 'httpd' package, configure
    it to start at boot and run the service immediately.
    '''

    # Connect to the remote (or local) OpenLMI managed system
    hostname = None
    if len(argv) > 1:
        hostname = argv[1]

    c = establish_connection(hostname)
    ns = c.root.cimv2

    exit(6)

    # Install the 'httpd' package
    packages = sw.find_package(ns, name='httpd')

    package = packages.next()

    res = sw.install_package(ns, package)
    if not res:
        stderr.write("Could not install package\n")
        exit(2)

    # Enable the service to start at boot
    try:
        service.enable_service(ns, 'httpd')
    except:
        stderr.write("Could not configure httpd to start at boot\n")
        exit(3)

    # Start the webserver service
    try:
        service.start_service(ns, 'httpd')
    except:
        stderr.write("Could not start httpd service\n")
        exit(4)

main(argv)
