#!/bin/sh

# =======================================================================================
# Copy a database on Kodi MariaDB container: for backup/restore operations
# =======================================================================================

this=$(basename "$0")

if [ "$#" -ne 2 ]
then
  echo "Usage: $this SOURCE_DB DEST_DB"
  exit 1
fi

SOURCE_DB=$1
DEST_DB=$2

# - Dump source database to temp SQL file
# - Replace references from source to destination database in temp SQL file
# - Create destination database from temp SQL file
(source .env; docker compose exec -T kodi-mariadb sh -c "\
    echo Dumping database \'$SOURCE_DB\' ... && \
    mysqldump -u $KODI_DB_USER -p'$KODI_DB_PASSWORD' --databases $SOURCE_DB --add-drop-database --add-drop-table --add-drop-trigger --routines --triggers >/root/temp_backup_db.sql && \
    echo Replacing references ... && \
    sed -i 's/$SOURCE_DB/$DEST_DB/g' /root/temp_backup_db.sql && \
    echo Creating database \'$DEST_DB\' ... && \
    mysql -u $KODI_DB_USER -p'$KODI_DB_PASSWORD' </root/temp_backup_db.sql && \
    echo DONE ! && \
    rm /root/temp_backup_db.sql")
