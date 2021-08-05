#!/bin/sh

# =======================================================================================
# Upgrade portainer
# =======================================================================================

# Set long timeout to prevent errors with 'docker-compose up' command (slow on MyCloud EX2 Ultra)
COMPOSE_HTTP_TIMEOUT=600

# Pull latest version
docker pull portainer/portainer-ce

# Stop and remove existing container (if needed)
docker stop portainer 2> /dev/null || true
docker rm portainer 2> /dev/null || true

# Run new container
docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce