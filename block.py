#!/usr/bin/python

import re
import subprocess
import sys
import netaddr

IPV4_REGEX = "\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"

PREAUTH_DISCONNECT='Disconnected from (' + IPV4_REGEX + ') port \d+ \[preauth\]'
PREAUTH_AUTH_DISCONNECT=(
    'Disconnected from authenticating user \S+ (' + IPV4_REGEX + ') port \d+ \[preauth\]')
PREAUTH_INVALID_USER_DISCONNECT=(
    'Disconnected from invalid user \S+ (' + IPV4_REGEX + ') port \d+ \[preauth\]')

BAN_REGEXES=[
    PREAUTH_DISCONNECT,
    PREAUTH_AUTH_DISCONNECT,
    PREAUTH_INVALID_USER_DISCONNECT
]

IPSET_INVALID=netaddr.IPSet([
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "172.16.0.0/12",
    "192.168.0.0/16", "169.254.0.0/16", "255.0.0.0/8",
    "224.0.0.0/4"])

IPSET_BLACKLIST="SW_DBL4"

def LogToIpSet(fp):
    ips = netaddr.IPSet()
    regexes = [re.compile(r) for r in BAN_REGEXES]
    while True:
        line = fp.readline()
        if not line:
            break
        line = line.rstrip()
        for regex in regexes:
            match = regex.search(line)
            if match:
                 ips.add(match.group(1))
    return ips


def LinuxIpSetToIpSet(name):
    command = ["ipset", "-o", "plain", "list", name]
    ipv4_regex = re.compile("^(" + IPV4_REGEX + ")")
    ips = netaddr.IPSet()
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = popen.communicate()
    for line in stdout.split("\n"):
        match = ipv4_regex.search(line)
        if match:
            ips.add(match.group(1))
    return ips


def __main__(argv):
    blocked_ips = LinuxIpSetToIpSet(IPSET_BLACKLIST)
    log_ips = LogToIpSet(sys.stdin)
    new_to_block_ips = log_ips - blocked_ips - IPSET_INVALID
    for ip in sorted(new_to_block_ips):
        print ip
    return 0


if __name__ == "__main__":
    sys.exit(__main__(sys.argv))
