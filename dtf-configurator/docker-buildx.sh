#!/bin/sh
set -eu

DOCKER_IMAGE_TAG=ahuh/dtf-configurator:latest
NO_CACHE=false

if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != "--no-cache" ]; }; then
    echo "Usage: $0 [--no-cache]" >&2
    exit 2
fi

if [ "${1:-}" = "--no-cache" ]; then
    NO_CACHE=true
fi

# Remove a builder left behind by an interrupted build.
if docker buildx inspect multiarch-builder >/dev/null 2>&1; then
    if [ "${NO_CACHE}" = true ]; then
        docker buildx prune --builder multiarch-builder --all --force
    fi
    docker buildx use default
    docker buildx rm --force multiarch-builder
fi

docker buildx create --use \
    --name multiarch-builder \
    --driver docker-container \
    --buildkitd-config ../buildkitd.toml
docker buildx build --platform=linux/amd64,linux/arm64,linux/386,linux/arm/v7,linux/arm/v6 -t ${DOCKER_IMAGE_TAG} --push .
docker buildx use default
docker buildx rm multiarch-builder