#!/bin/sh

# =======================================================================================
# Launch the Docker Torrent Factory
# =======================================================================================

source .env

# - Pull new images from docker hub (update)
# - Start containers in detached mode
docker compose pull ${DTF_CONTAINERS} && \
docker compose up -d ${DTF_CONTAINERS}