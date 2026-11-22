#!/bin/sh
set -eu

DOCKER_IMAGE_TAG=ahuh/pyphotorg:latest

# Remove a builder left behind by an interrupted build.
if docker buildx inspect multiarch-builder >/dev/null 2>&1; then
    docker buildx use default
    docker buildx rm multiarch-builder
fi

docker buildx create --use \
    --name multiarch-builder \
    --driver docker-container \
    --buildkitd-config ../buildkitd.toml
docker buildx build --platform=linux/amd64,linux/arm64,linux/386,linux/arm/v7,linux/arm/v6 -t ${DOCKER_IMAGE_TAG} --push .
docker buildx use default
docker buildx rm multiarch-builder