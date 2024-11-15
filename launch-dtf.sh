#!/bin/sh

# =======================================================================================
# Launch the Docker Torrent Factory
# =======================================================================================

# Set long timeout to prevent errors with 'docker compose up' command (slow on MyCloud EX2 Ultra)
export COMPOSE_HTTP_TIMEOUT=600

# Select containers to activate
export DTF_CONTAINERS="transmission-openvpn joal medusa jackett kodi-mariadb nginx minidlna pyphotorg"

# - Pull new images from docker hub (update)
# - Start containers in detached mode
docker compose pull ${DTF_CONTAINERS} && \
docker compose up -d ${DTF_CONTAINERS}