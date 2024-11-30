#!/bin/sh

# =======================================================================================
# Launch the Docker Torrent Factory monitor 
# =======================================================================================

source .env

# - Pull new images from docker hub (update)
# - Start container and wait until configuration finished
docker compose -p dtf-monitor -f docker-compose-monitor.yml pull && \
docker compose -p dtf-monitor -f docker-compose-monitor.yml up -d