#!/bin/sh

# =======================================================================================
# Reindex media files on MiniDLNA container
# =======================================================================================

# Set long timeout to prevent errors with 'docker-compose up' command (slow on MyCloud EX2 Ultra)
COMPOSE_HTTP_TIMEOUT=600

# - Delete cache
# - Kill main process to force restart
docker-compose exec -T minidlna sh -c 'rm -rf /minidlna/* && kill 1'