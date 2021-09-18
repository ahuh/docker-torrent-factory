#!/bin/sh
docker buildx create --name multiarch-builder --use
docker buildx build --platform=linux/amd64,linux/arm64,linux/386,linux/arm/v7,linux/arm/v6 -t ahuh/pyphotorg:latest --push .
docker buildx use default
docker buildx rm multiarch-builder