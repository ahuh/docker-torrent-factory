#!/bin/sh

# =======================================================================================
# Terminate the Docker Torrent Factory monitor 
# =======================================================================================

source .env

# - Stop and remove containers
docker compose -p dtf-monitor -f docker-compose-monitor.yml down