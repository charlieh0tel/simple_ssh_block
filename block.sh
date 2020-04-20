#!/bin/sh

for ip in $(./block.py < /var/log/auth.log); do
    shorewall blacklist "${ip}"
done
