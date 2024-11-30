#!/bin/sh

# =======================================================================================
# Reindex media files on MiniDLNA container
# =======================================================================================

source .env

# - Delete cache
# - Kill main process to force restart
docker compose exec -T minidlna sh -c 'rm -rf /minidlna/* && kill 1'