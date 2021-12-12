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
$ ./docker-buildx.sh
```
WARNING: for Windows environment, do not execute buildx in Windows but directly in WSL 2