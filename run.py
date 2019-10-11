import requests                                   # For RESTful calls
from requests.auth import HTTPBasicAuth           # For initial authentication w/ DNAC
requests.packages.urllib3.disable_warnings()      # Disable warnings. Living on the wild side..
import logging.handlers
import argparse
import time

def getAPICCookie():
    url = 'https://' + args.apic_ip + ':' + args.apic_port + '/api/aaaLogin.json'
    body = {"aaaUser": {"attributes": {"name": args.apic_user, "pwd": args.apic_password}}}
    res = requests.post(url=url, json=body, verify=False)
    rawcookie = res.cookies['APIC-cookie']
    print("Got cookie: " + rawcookie)
    return rawcookie

def getAPICAudit(rawcookie):
    cookies = {}
    cookies['APIC-cookie'] = rawcookie
    url = 'https://' + args.apic_ip + ':' + args.apic_port + '/api/node/class/aaaModLR.json?query-target-filter=not(wcard(aaaModLR.dn,"_ui"))&order-by=aaaModLR.created|desc'
    res = requests.get(url=url, cookies=cookies, verify=False)
    return res.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cisco-dnac-platform-audit-by-syslog version 1.3.1')
    parser.add_argument('--syslog_ip', help="please enter the IP address of the syslog server")
    parser.add_argument('--syslog_port', help="please enter the UDP of the syslog server, default port is 514", type=int, default=514)
    parser.add_argument('--apic_ip', help="please enter the IP of the Cisco APIC")
    parser.add_argument('--apic_port', help="please enter the port of the Cisco APIC, default port is 443", type=str, default="443")
    parser.add_argument('--apic_user', help="please enter the username for Cisco APIC, default user is admin", default="admin")
    parser.add_argument('--apic_password', help="please enter the password for Cisco APIC")
    parser.add_argument('--period', help="please enter the polling period (in minutes), default is 5", type=int, default=5)
    args = parser.parse_args()

    # Arguments verification:
    if args.syslog_ip is None:
        raise Exception("Sorry, no syslog server is set")
    if args.apic_ip is None:
        raise Exception("Sorry, no APIC is set")
    if args.apic_password is None:
        raise Exception("Sorry, no password for APIC is set")

    # Creating the logger
    apic_logger = logging.getLogger('apic_logger')
    apic_logger.setLevel(logging.INFO)

    #Creating the logging handler, directing to the syslog server
    handler = logging.handlers.SysLogHandler(address = (args.syslog_ip,args.syslog_port))
    apic_logger.addHandler(handler)
    print("\n ************************************************* \n")

    lastEventId = ""
    lastAuditCount = ""

# Entering an infinite loop

    while True:

        # Getting the latest Audit log
        print("Getting the latest audit log...")
        rawcookie = getAPICCookie()
        audit = getAPICAudit(rawcookie)
        duplicate = False

        if (audit['totalCount'] == lastAuditCount):
            duplicate = True
        else:
            # Going through the events (until we reach the last event of the previous pull)
            for event in audit['imdata']:
                if event['aaaModLR']['attributes']['id'] == lastEventId:
                    duplicate = True
                elif not duplicate:
                    eventTime = event['aaaModLR']['attributes']['created']
                    eventId = event['aaaModLR']['attributes']['id']
                    eventUser = event['aaaModLR']['attributes']['user']
                    eventAffected = event['aaaModLR']['attributes']['affected']
                    eventDesc = event['aaaModLR']['attributes']['descr']
                    data = "%s | Event ID: %s | User: %s | Affected: %s | Description: %s" % (eventTime, eventId, eventUser, eventAffected, eventDesc)

                    # Send the event via syslog
                    apic_logger.info(str(data))

        # Mark the newest event as the last one, for the next loop
        lastEventId = audit['imdata'][0]['aaaModLR']['attributes']['id']

        if duplicate:
            print("\nreached the last event from the previous poll.")
        print("\nFinished this poll, waiting for the next...")

        # Sleep until next time
        time.sleep(60*args.period)
