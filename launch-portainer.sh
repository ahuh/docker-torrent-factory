#!/bin/sh

# =======================================================================================
# Launch portainer
# =======================================================================================

# Set long timeout to prevent errors with 'docker-compose up' command (slow on MyCloud EX2 Ultra)
export COMPOSE_HTTP_TIMEOUT=600

# - Pull new images from docker hub (update)
# - Start container and wait until configuration finished
docker-compose -p torrent-factory-portainer -f docker-compose-portainer.yml pull && docker-compose -p torrent-factory-portainer -f docker-compose-portainer.yml up -d