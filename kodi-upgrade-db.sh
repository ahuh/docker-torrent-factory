#!/bin/sh

# =======================================================================================
# Upgrade database on Kodi MariaDB container: to do after each MariaDB version upgrade !
# =======================================================================================

# - Fix too permissive permissions on MariaDB config file
# - Upgrade database for the current MariaDB version
(source .env; docker compose exec -T kodi-mariadb sh -c "chmod 664 /config/custom.cnf && mariadb-upgrade -u root -p'$KODI_DB_ROOT_PASSWORD'")