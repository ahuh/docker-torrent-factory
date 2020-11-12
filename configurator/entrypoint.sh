#!/usr/bin/env bash

# Set user for impersonation
. /scripts/userSetup.sh

# ========================================================================
# Variables
MEDUSA_CONFIG_DIR=/config/medusa
MEDUSA_CONFIG_FILE=${MEDUSA_CONFIG_DIR}/config.ini
COUCHPOTATO_CONFIG_DIR=/config/couchpotato
COUCHPOTATO_CONFIG_FILE=${COUCHPOTATO_CONFIG_DIR}/config.ini
NGINX_CONFIG_DIR=/config/nginx
NGINX_CONFIG_FILE=${NGINX_CONFIG_DIR}/nginx.conf
NGINX_HTPASSWD_FILE=${NGINX_CONFIG_DIR}/passwords
NGINX_LOGS_DIR=/config/nginx/logs
MINIDLNA_CONFIG_DIR=/config/minidlna
SSL_CONFIG_DIR=/config/ssl
TRANSMISSION_CONFIG_DIR=/config/transmission

# ========================================================================
echo "Creating / Updating configuration dirs ..."

mkdir -p ${MEDUSA_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${MEDUSA_CONFIG_DIR}
mkdir -p ${COUCHPOTATO_CONFIG_DIR}
chown -R ${RUN_AS}:${RUN_AS} ${COUCHPOTATO_CONFIG_DIR}
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
echo "Creating / Updating CouchPotato configuration file ..."

# Concat movies dirs
COUCHPOTATO_MOVIES_DIR_CONCAT=${COUCHPOTATO_MOVIES_MAIN_DIR}
for VAR in $(env); do
	if [[ "$VAR" =~ ^COUCHPOTATO_MOVIES_DIR_ ]]; then
		VAR_VALUE=$(echo "$VAR" | sed -r "s/.*=(.*)/\\1/g")
		COUCHPOTATO_MOVIES_DIR_CONCAT="${COUCHPOTATO_MOVIES_DIR_CONCAT}::${VAR_VALUE}"
	fi
done

# Create config file if not exists
touch ${COUCHPOTATO_CONFIG_FILE}
chown ${RUN_AS}:${RUN_AS} ${COUCHPOTATO_CONFIG_FILE}

# Configure file
# - General section
if [ "${COUCHPOTATO_USE_HTTP_PROXY}" = true ] ; then
	crudini --set ${COUCHPOTATO_CONFIG_FILE} core use_proxy 1
	crudini --set ${COUCHPOTATO_CONFIG_FILE} core proxy_server "transmission-openvpn:8789"
else
	crudini --set ${COUCHPOTATO_CONFIG_FILE} core use_proxy 0
	crudini --del ${COUCHPOTATO_CONFIG_FILE} core proxy_server
fi
crudini --set ${COUCHPOTATO_CONFIG_FILE} manage enabled 1
crudini --set ${COUCHPOTATO_CONFIG_FILE} manage library "${COUCHPOTATO_MOVIES_DIR_CONCAT}"
crudini --set ${COUCHPOTATO_CONFIG_FILE} renamer enabled 1
crudini --set ${COUCHPOTATO_CONFIG_FILE} renamer file_action copy
crudini --set ${COUCHPOTATO_CONFIG_FILE} renamer from "${COUCHPOTATO_TORRENT_DOWNLOAD_DIR}"
crudini --set ${COUCHPOTATO_CONFIG_FILE} renamer to "${COUCHPOTATO_MOVIES_MAIN_DIR}"
crudini --set ${COUCHPOTATO_CONFIG_FILE} searcher preferred_method torrent
crudini --set ${COUCHPOTATO_CONFIG_FILE} transmission enabled 1
crudini --set ${COUCHPOTATO_CONFIG_FILE} transmission directory "${COUCHPOTATO_TORRENT_DOWNLOAD_DIR}"
crudini --set ${COUCHPOTATO_CONFIG_FILE} transmission host "http://transmission-openvpn:9091"
crudini --set ${COUCHPOTATO_CONFIG_FILE} transmission rpc_url transmission
crudini --set ${COUCHPOTATO_CONFIG_FILE} updater automatic 0

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
