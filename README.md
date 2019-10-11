# cisco-aci-audit-exporter
This script will pull ACI's audit log every <defined period of time>, in order to
export it to an external program/platform.
Initial version is for syslog, later I'll add Webex Teams.

## How to setup
```
docker run -d obrigg/cisco-aci-audit-exporter --apic_ip "APIC-CLUSTER-IP" --apic_password "APIC-PASSWORD" --syslog_ip "SYSLOG-SERVER-IP"
```
### Optional Arguments:
* --apic_port: If different than 443.
* --apic_user: If different than "admin".
* --syslog_port: If different than 514.
* --period: pulling time, if different than 5 minutes.
