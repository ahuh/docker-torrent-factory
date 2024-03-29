#!/bin/sh

# =======================================================================================
# Launch the Docker Torrent Factory
# =======================================================================================

# Set long timeout to prevent errors with 'docker compose up' command (slow on MyCloud EX2 Ultra)
export COMPOSE_HTTP_TIMEOUT=600

# - Pull new images from docker hub (update)
# - Start containers in detached mode
docker compose pull && \
docker compose up -d