#!/usr/bin/env bash

# Set user for impersonation
. /scripts/userSetup.sh

# ========================================================================
# Variables
JOAL_TMP_DIR=/tmp/joal/clients
JOAL_CONFIG_DIR=/config/joal
JOAL_TORRENTS_DIR=${JOAL_CONFIG_DIR}/torrents
JOAL_CLIENTS_DIR=${JOAL_CONFIG_DIR}/clients
JOAL_CONFIG_FILE=${JOAL_CONFIG_DIR}/config.json
MEDUSA_CONFIG_DIR=/config/medusa
MEDUSA_CONFIG_FILE=${MEDUSA_CONFIG_DIR}/config.ini
KODI_MARIADB_CONFIG_DIR=/config/kodi-mariadb
KODI_MARIADB_CONFIG_INITDB_DIR=${KODI_MARIADB_CONFIG_DIR}/initdb.d
KODI_MARIADB_CONFIG_FILE=${KODI_MARIADB_CONFIG_INITDB_DIR}/kodi.sql
NGINX_CONFIG_DIR=/config/nginx
NGINX_CONFIG_FILE=${NGINX_CONFIG_DIR}/nginx.conf
NGINX_HTPASSWD_FILE=${NGINX_CONFIG_DIR}/passwords
NGINX_LOGS_DIR=/config/nginx/logs
MINIDLNA_CONFIG_DIR=/config/minidlna
RADARR_CONFIG_DIR=/config/radarr
SSL_CONFIG_DIR=/config/ssl
TRANSMISSION_CONFIG_DIR=/config/transmission

# ========================================================================
echo "Creating / Updating configuration dirs ..."

mkdir -p ${JOAL_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${JOAL_CONFIG_DIR}
mkdir -p ${JOAL_TORRENTS_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${JOAL_TORRENTS_DIR}
cp -r ${JOAL_TMP_DIR} ${JOAL_CLIENTS_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${JOAL_CLIENTS_DIR}
mkdir -p ${MEDUSA_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${MEDUSA_CONFIG_DIR}
mkdir -p ${RADARR_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${RADARR_CONFIG_DIR}
mkdir -p ${KODI_MARIADB_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${KODI_MARIADB_CONFIG_DIR}
mkdir -p ${KODI_MARIADB_CONFIG_INITDB_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${KODI_MARIADB_CONFIG_INITDB_DIR}
mkdir -p ${NGINX_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${NGINX_CONFIG_DIR}
mkdir -p ${NGINX_LOGS_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${NGINX_LOGS_DIR}
mkdir -p ${MINIDLNA_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${MINIDLNA_CONFIG_DIR}
mkdir -p ${SSL_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${SSL_CONFIG_DIR}
mkdir -p ${TRANSMISSION_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${TRANSMISSION_CONFIG_DIR}

echo "... DONE !"
echo ""

# ========================================================================
echo "Creating / Updating JOAL configuration file ..."

# Configure file
touch ${JOAL_CONFIG_FILE}
chown ${RUN_AS}:${RUN_AS} ${JOAL_CONFIG_FILE}
cat /resources/config.json > ${JOAL_CONFIG_FILE}

echo "... DONE !"
echo ""

# ========================================================================
echo "Creating / Updating Kodi MariaDB configuration file ..."

# Configure file
touch ${KODI_MARIADB_CONFIG_FILE}
chown ${RUN_AS}:${RUN_AS} ${KODI_MARIADB_CONFIG_FILE}
cat /resources/kodi.sql > ${KODI_MARIADB_CONFIG_FILE}

echo "... DONE !"
echo ""

# ========================================================================
echo "Creating / Updating Medusa configuration file ..."

# Concat tvshows dirs
MEDUSA_TVSHOWS_DIR_CONCAT=${MEDUSA_TVSHOWS_MAIN_DIR}
for VAR in $(env); do
	if [[ "$VAR" =~ ^MEDUSA_TVSHOWS_DIR_ ]]; then
		VAR_VALUE=$(echo "$VAR" | sed -r "s/.*=(.*)/\\1/g")
		MEDUSA_TVSHOWS_DIR_CONCAT="${MEDUSA_TVSHOWS_DIR_CONCAT}, ${VAR_VALUE}"
	fi
done

# Create config file if not exists
touch ${MEDUSA_CONFIG_FILE}
chown ${RUN_AS}:${RUN_AS} ${MEDUSA_CONFIG_FILE}

# Configure file
# - General section
crudini --set ${MEDUSA_CONFIG_FILE} General handle_reverse_proxy 1
crudini --set ${MEDUSA_CONFIG_FILE} General use_torrents 1
crudini --set ${MEDUSA_CONFIG_FILE} General process_automatically 1
if [ "${MEDUSA_USE_HTTP_PROXY}" = true ] ; then
	crudini --set ${MEDUSA_CONFIG_FILE} General proxy_indexers 1
	crudini --set ${MEDUSA_CONFIG_FILE} General proxy_setting "http://transmission-openvpn:8789"
else
	crudini --set ${MEDUSA_CONFIG_FILE} General proxy_indexers 0
	crudini --del ${MEDUSA_CONFIG_FILE} General proxy_setting
fi
crudini --set ${MEDUSA_CONFIG_FILE} General root_dirs "0, ${MEDUSA_TVSHOWS_DIR_CONCAT}"
crudini --set ${MEDUSA_CONFIG_FILE} General torrent_method transmission
crudini --set ${MEDUSA_CONFIG_FILE} General tv_download_dir "${MEDUSA_TORRENT_DOWNLOAD_DIR}"
# - Torrent section
crudini --set ${MEDUSA_CONFIG_FILE} TORRENT torrent_auth_type none
crudini --set ${MEDUSA_CONFIG_FILE} TORRENT torrent_host "http://transmission-openvpn:9091/"
crudini --set ${MEDUSA_CONFIG_FILE} TORRENT torrent_path "${MEDUSA_TORRENT_DOWNLOAD_DIR}"
crudini --set ${MEDUSA_CONFIG_FILE} TORRENT torrent_rpcurl transmission
crudini --set ${MEDUSA_CONFIG_FILE} TORRENT torrent_seed_location "${MEDUSA_TORRENT_SEED_DIR}"

echo "... DONE !"
echo ""

# ========================================================================
echo "Creating / Updating nginx configuration file ..."

# Password file
echo "${NGINX_PASSWORD}" | htpasswd -i -c ${NGINX_HTPASSWD_FILE} ${NGINX_USERNAME}
chown ${RUN_AS}:${RUN_AS} ${NGINX_HTPASSWD_FILE}

# Configure file
touch ${NGINX_CONFIG_FILE}
chown ${RUN_AS}:${RUN_AS} ${NGINX_CONFIG_FILE}
cat /resources/nginx.conf > ${NGINX_CONFIG_FILE}

echo "... DONE !"
echo ""

echo "Configuration finished !"
echo ""
