#!/bin/sh

# =======================================================================================
# Launch the Docker Torrent Factory configurator
# =======================================================================================

source .env

# - Pull new image from docker hub (update)
# - Start container and wait until configuration finished
# - Remove container at the end
docker compose -p dtf-configurator -f docker-compose-configurator.yml pull && \
docker compose -p dtf-configurator -f docker-compose-configurator.yml up && \
docker compose -p dtf-configurator -f docker-compose-configurator.yml down