#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import os
import os.path
import socket
import subprocess
import time
import traceback
from pprint import pprint
from zapv2 import ZAPv2


running_in_docker = os.path.exists('/.dockerenv')
time_format = "%a %b %d %H:%M%S %Y"

# Change to match the API key set in ZAP, or use None if the API key is disabled
apikey = None

# By default, ZAP API client will connect to port 8080
zap = ZAPv2(apikey=apikey)
# Use the line below if ZAP is not listening on port 8080, for example, if listening on port 8090
# zap = ZAPv2(apikey=apikey, proxies={'http': 'http://127.0.0.1:8090', 'https': 'http://127.0.0.1:8090'})

parser = argparse.ArgumentParser()

parser.add_argument('-t', action='store', dest='target', help='Target URL')
parser.add_argument('-o', action='store', dest='openapi_url', help='OpenAPI definition URL')
args = parser.parse_args()

def main(argv):

    base_dir = ''
    port = 0
    report_html = ''
    zap_ip = 'localhost'

if running_in_docker:
    base_dir = '/zap/wrk/'

if port == 0:
    while True:
        port = randit(32768, 61000)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not (sock.connect_ex(('127.0.0.1', port)) == 0):
            break

logging.debug('Using port: ') + str(port))

if running_in_docker:
    try:
      logging.debug ('Starting ZAP')
      params = ['zap-x.sh', '-daemon',
                '-port', str(port),
                '-host', '0.0.0.0',
                '-config', 'api.disablekey=true',
                '-config', 'api.addrs.addr.name=.*',
                '-config', 'api.addrs.addr.regex=true',
                '-config', 'spider.maxDuration=' + str(mins),
                '-addonupdate',
                '-addoninstall', 'openapi']	# In case we're running in the stable container

      with open('zap.out', "w") as outfile:
          subprocess.Popen(params, stdout=outfile)
zap.core.new_session()

zap._request(zap.base + 'openapi/action/importUrl/', {'url': args.openapi_url})

# Proxy a request to the target so that ZAP has something to deal with
timestamp = datetime.datetime.today()
print str(timestamp) + ' - ' + 'Accessing target %s' % args.target
zap.urlopen(args.target)
# Give the sites tree a chance to get updated
time.sleep(2)

print str(timestamp) + ' - ' + 'Active Scanning target %s' % args.target
scanid = zap.ascan.scan(args.target)
while (int(zap.ascan.status(scanid)) < 100):
    # Loop until the scanner has finished
    print str(timestamp) + ' - ' + 'Scan progress %: ' + zap.ascan.status(scanid)
    time.sleep(5)

print str(timestamp) + ' - ' + 'Active Scan completed'

# Report the results
print str(timestamp) + ' - ' + 'Writing HTML Report'
f = open('zap-report.html', 'w')
f.write(zap.core.htmlreport())

# print 'Hosts: ' + ', '.join(zap.core.hosts)
# print 'Alerts: '
pprint(zap.core.alerts())
