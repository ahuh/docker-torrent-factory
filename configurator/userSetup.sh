#!/usr/bin/env bash

# More/less taken from https://github.com/linuxserver/docker-baseimage-alpine/blob/3eb7146a55b7bff547905e0d3f71a26036448ae6/root/etc/cont-init.d/10-adduser

RUN_AS=root

if [ -n "$PUID" ] && [ ! "$(id -u root)" -eq "$PUID" ]; then
    RUN_AS=abc
    if [ ! "$(id -u ${RUN_AS})" -eq "$PUID" ]; then usermod -o -u "$PUID" ${RUN_AS} ; fi
    if [ ! "$(id -g ${RUN_AS})" -eq "$PGID" ]; then groupmod -o -g "$PGID" ${RUN_AS} ; fi

    echo "Setting owner for working dirs to ${PUID}:${PGID}"
    chown -R ${RUN_AS}:${RUN_AS} /config \
      /resources \
      /scripts
fi

echo "
-------------------------------------
operations will run as
-------------------------------------
User name:   ${RUN_AS}
User uid:    $(id -u ${RUN_AS})
User gid:    $(id -g ${RUN_AS})
-------------------------------------
"

export PUID
export PGID
export RUN_AS