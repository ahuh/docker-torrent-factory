#!/bin/sh

# =======================================================================================
# Launch the configurator for torrent factory
# =======================================================================================

# Set long timeout to prevent errors with 'docker-compose up' command (slow on MyCloud EX2 Ultra)
export COMPOSE_HTTP_TIMEOUT=600

# - Pull new image from docker hub (update)
# - Start container and wait until configuration finished
docker-compose -p torrent-factory-configurator -f docker-compose-configurator.yml pull && docker-compose -p torrent-factory-configurator -f docker-compose-configurator.yml up