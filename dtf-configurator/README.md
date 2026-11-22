# Docker Torrent Factory Configurator
Configurator for Docker Torrent Factory.

See project home page: https://github.com/ahuh/docker-torrent-factory

## HOW-TOs

### Build and push image

Build (for current arch):
```bash
$ ./docker-build.sh
```

Push (for current arch):
```bash
$ ./docker-push.sh
```

Or with buildx (build & push multiarch):
```bash
$ ./docker-buildx.sh [--no-cache]
```
Pass `--no-cache` to prune all cache from an existing `multiarch-builder` before removing it and starting the build with a fresh builder.

WARNINGS:
* `docker buildx` does not work in QNAP NAS: install and execute in WSL instead
* For Windows environment, do not execute buildx in Windows but directly in WSL
* Multi-platform builds use the shared `buildkitd.toml` configuration to limit BuildKit parallelism to 4 operations