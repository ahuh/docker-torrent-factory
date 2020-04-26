# Docker Torrent Factory
Docker image dedicated to ARMv7 processors, hosting a Medusa server with WebUI.<br />
<br />
This project is based on existing projects, combined and modified to work on ARMv7 WD My Cloud EX2 Ultra NAS.<br />
See GitHub repositories:
* https://github.com/edv/docker-sickrage
* https://github.com/haugene/docker-transmission-openvpn
<br />

## Installation

### Prerequisite

* Arrêter docker : `/usr/sbin/docker_daemon.sh stop`
* Télécharger sur : https://wdcommunity.com/
* Installer l'application via web UI MyCloud : MyCloudEX2Ultra_entware_1.05.bin
* Installer l'application via web UI MyCloud : MyCloudEX2Ultra_docker_19.03.5.bin
* Installer docker-compose : bridage à v1.23.x car à partir de 1.24 nécessite build librairies crypto en arm (pas possible avec opkg car pas de package dev ?)
```bash
$ opkg update
$ opkg install python3-pip
$ pip3 install --upgrade pip
$ pip install setuptools
$ pip install docker-compose~=1.23.0
```

* Install and upgrade python3 and pip :
```bash
$ # Install on MyCloud EX2 Ultra
$ opkg update
$ opkg install python3-pip
$ pip3 install --upgrade pip
```
* Install docker-compose :
```bash
$ pip install setuptools
$ # Install on MyCloud EX2 Ultra : limit to 1.23.x, because >=1.24 requires to build crypto libs in ARM (not possible with opkg because of lack of dev packages)
$ pip install docker-compose~=1.23.0
```
* Install crudini : download custom 0.9.3 (first version with python3 support, not available yet in pypi)
```bash
$ # Install on MyCloud EX2 Ultra
$ pip install https://github.com/pixelb/crudini/releases/download/0.9.3/crudini-0.9.3.tar.gz
$ # Install on Raspbian
$ pip install crudini
```

### Install

```bash
shares/P2P/tools
├── couchpotato			# Contains CouchPotato configuration, database, cache and logs
│	├── config.ini		# CouchPotato configuration file (use configurator to initialize, use Web UI for full setup)
│	└── ...
├── medusa				# Contains Medusa configuration, database, cache and logs
│	├── config.ini		# Medusa configuration file (use configurator to setup, use Web UI for full setup)
│	└── ...
├── minidlna			# Contains MiniDLNA database cache (delete content to force reindex)
│	└── ...
├── nginx				# Contains nginx configuration, passwords and logs
│	├── nginx.conf		# nginx configuration file (use configurator to setup)
│	├── passwords		# nginx credentials for basic authentication (use configurator to setup)
│	└── logs			# nginx logs
├── ssl					# Contains certificates for nginx HTTPS access 
│	└── ...				# **GENERATE FILES .crt AND .key HERE**
└── transmission		# Contains Transmission configuration, cache and logs
	├── settings.json	# Transmission configuration file (do not modify, automatically configured by transmission-openvpn service)
	└── ...
```

```bash
storage
├── _hd1			# External hard-drive #1
│	├── Enfants		# Children videos
│	│	├── Films	# Children movies on HD1, managed by CouchPotato
│	│	├── Series	# Children TV shows on HD1, managed by Medusa
│	│	└── ...
│	├── Films		# Movies on HD1, managed by CouchPotato
│	├── Series		# TV shows on HD1, managed by Medusa
│	└── ...
├── ...
├── complete		# Downloaded torrents, published with MiniDLNA
│	├── couchpotato	# Downloaded torrents, managed by CouchPotato 
│	├── medusa		# Downloaded torrents, managed by Medusa
│	└── seed		# Seeding torrents
├── incomplete		# Currently downloading torrents
├── watch			# Watch directory for *.torrent files
├── ...
├── Backup			# Old personal photos & videos, published with MiniDLNA and published with MiniDLNA
├── Films			# Movies on NAS, managed by CouchPotato and published with MiniDLNA
├── MP3				# Music on NAS, published with MiniDLNA
├── Photos			# Personal photos & videos to publish with MiniDLNA
├── Series			# TV shows on NAS, managed by Medusa and published with MiniDLNA
└── Videos			# Misc videos on NAS, published with MiniDLNA
```

### Preparation
Before running container, you have to retrieve UID and GID for the user used to mount your tv shows directory:
* Get user UID:
```
$ id -u <user>
```
* Get user GID:
```
$ id -g <user>
```
The container will run impersonated as this user, in order to have read/write access to the tv shows directory.

### Run container in background
```
$ docker run --name medusa --restart=always  \
		--add-host=dockerhost:<docker host IP> \
		--dns=<ip of dns #1> --dns=<ip of dns #2> \
		-d \
		-p <webui port>:8081 \
		-v <path to Medusa configuration dir>:/config \
		-v <path to Medusa data dir>:/storage \
		-v <path to tv shows dir>:/tvshowsdir \
		-v <path to downloaded files to process>:/postprocessingdir \
		-v /etc/localtime:/etc/localtime:ro \
		-e "AUTO_UPDATE=<auto update Medusa at first start [true/false]>"
		-e "TORRENT_MODE=<transmission or qbittorrent>" \
		-e "TORRENT_PORT=<port of the torrent client>" \
		-e "TORRENT_LABEL=<label to use for Medusa in torrent client>" \
		-e "PROXY_PORT=<squid3 proxy port to use (leave empty to disable)>" \
		-e "PUID=<user uid>" \
		-e "PGID=<user gid>" \
		ahuh/arm-medusa
```
or
```
$ ./docker-run.sh medusa ahuh/arm-medusa
```
(set parameters in `docker-run.sh` before launch)

### Configure Medusa
The container will use volumes directories to manage tv shows files, to retrieve downloaded files, and to store data and configuration files.<br />
<br />
You have to create these volume directories with the PUID/PGID user permissions, before launching the container:
```
/tvshowsdir
/postprocessingdir
/config
/storage
```

The container will automatically create a `config.ini` file in the Medusa configuration dir (only if none was present before).<br />
* The following parameters will be automatically modified at launch for compatibility with the Docker container:
```
[General]
...
root_dirs = 0|/tvshowsdir
tv_download_dir = /postprocessingdir
unrar_tool = unrar
```
* Depending on the torrent client Docker container selected (transmission or qbittorrent), these parameters will be automatically modified at launch:
```
[General]
...
use_torrents = 1
torrent_method = ${TORRENT_MODE}
process_automatically = 1
handle_reverse_proxy = 1
...
[TORRENT]
...
torrent_auth_type = none
torrent_host = http://torrent:${TORRENT_PORT}/
torrent_path = /downloaddir/${TORRENT_LABEL}
```
* If a `PROXY_PORT` var is specified, the squid3 hosted on the Docker ARM TranSquidVpn container will be used for searches and indexers in Medusa. These parameters will be automatically modified at launch:
```
[General]
...
proxy_setting = http://dockerhost:${PROXY_PORT}
proxy_indexers = 1
```
* If you use qBittorrent as torrent client, you have to access the search settings in Medusa WebUI, and input the username / password for authentication.

If you modified the `config.ini` file, restart the container to reload Medusa configuration:
```
$ docker stop medusa
$ docker start medusa
```
* At the first start of the container, Medusa will automatically be updated from GitHub.

## HOW-TOs

### Get a new instance of bash in running container
Use this command instead of `docker attach` if you want to interact with the container while it's running:
```
$ docker exec -it medusa /bin/bash
```
or
```
$ ./docker-bash.sh medusa
```

### Build image
```
$ docker build -t arm-medusa .
```
or
```
$ ./docker-build.sh arm-medusa
```
