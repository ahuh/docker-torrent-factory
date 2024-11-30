#!/bin/sh

# =======================================================================================
# Terminate the Docker Torrent Factory
# =======================================================================================

source .env

# - Stop and remove containers
docker compose down ${DTF_CONTAINERS}