#!/usr/bin/env python

import argparse
import datetime
import time
from pprint import pprint
from zapv2 import ZAPv2


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
