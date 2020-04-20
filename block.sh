#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for ip in $("${DIR}"/block.py < /var/log/auth.log); do
    shorewall blacklist "${ip}"
done
