# Docker Torrent Factory
Docker compose dedicated to ARMv7 processors, hosting a complete torrent factory, or seedbox.<br />
<br />
This project is based on existing projects, combined and configured to work on the WD My Cloud EX2 Ultra NAS. It should also work for any ARMv7 device, such as another NAS or a Raspberry Pi.<br />
See GitHub repositories / Docker Hub images:
| Container | URLs |
|-----------|------|
| **Transmission-OpenVPN**<br />Torrent server secured by VPN connection | <ul><li>https://github.com/haugene/docker-transmission-openvpn</li><li>https://hub.docker.com/r/haugene/transmission-openvpn</li></ul>|
| **Medusa**<br />TV shows manager and auto-downloader, connected to torrent server | <ul><li>https://github.com/linuxserver/docker-medusa</li><li>https://hub.docker.com/r/linuxserver/medusa</li></ul>|
| **CouchPotato**<br />Movies manager and auto-downloader, connected to torrent server | <ul><li>https://github.com/linuxserver/docker-couchpotato</li><li>https://hub.docker.com/r/linuxserver/couchpotato</li></ul>|
| **nginx**<br />Reverse proxy, used to expose services as HTTPS with SSL certificates and basic authentication | <ul><li>https://github.com/nginxinc/docker-nginx</li><li>https://hub.docker.com/_/nginx</li></ul>|
| **MiniDLNA**<br />UPnP / DLNA service, used to publish media files on the local network | <ul><li>https://github.com/vladgh/docker_base_images/tree/master/minidlna</li><li>https://hub.docker.com/r/vladgh/minidlna</li></ul>|
| **Resilio Sync**<br />File sync service based on P2P, used to backup photos / videos from mobiles to NAS on the local network | <ul><li>https://www.resilio.com</li><li>https://hub.docker.com/r/resilio/sync/</li></ul>|

## How does it work ?
This repository contains a main docker-compose file, configured to launch each dedicated service (docker container). This diagram explains how it works:<br /><br />
![Architecture of the Docker Torrent Factory](./resources/docker-torrent-factory.png)

Another docker-compose file is provided to construct a configurator service, that you may use to automatically configure each service to work together. This one is a "one-shot" process: you may launch it one time before launching the main docker-compose file, in order to generate the configuration files for each service. Note that you still can configure each service with the dedicated web UI (Medusa, CouchPotato, etc), to do additional settings.

## Features
* TODO

## Prerequisites

### VPN subscription
You need a VPN subscription before installing the torrent factory. You will have to specify the VPN provider, user login and password to use in the OpenVPN service. See supported providers here: http://haugene.github.io/docker-transmission-openvpn/supported-providers/

### SSL certificates
If you wish to secure external access to your services web UIs with nginx, you will need to provide an SSL certificate. A self-signed certificate will do the trick, for example see this tutorial for generation: https://devcenter.heroku.com/articles/ssl-certificate-self. You will have to provide two files : `server.key` and `server.crt`.

### Docker installation
On WD MyCloud EX2 Ultra, you need to replace the old docker install by a fresh one, and then install docker-compose.
For this, follow these steps:
* Connect to the NAS with SSH as `root` user (see manual for details)
* Stop the docker daemon: `/usr/sbin/docker_daemon.sh stop`
* Download the following apps from the WD community site: https://wdcommunity.com/
  * Last version of Entware: `MyCloudEX2Ultra_entware_1.05.bin`
  * Last version of Docker: `MyCloudEX2Ultra_docker_19.03.5.bin`
* Install the downloaded apps using the MyCloud web UI: upload and install apps (see manual for details)
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
$ # Install on MyCloud EX2 Ultra : limit to 1.23.x, because >=1.24 requires to build crypto libs in ARM
$ #   (not possible with opkg because of lack of dev packages)
$ pip install docker-compose~=1.23.0
```

On other NAS / Raspberry Pi devices, just install last versions of docker and docker-compose.

## Installation

### Preparation
Before running the containers, you have to retrieve UID and GID for the user used to mount your directories (configuration, medias):
* Connect to the NAS with SSH as `root` user
* Go to the shared directories that contains the media files stored on your NAS: `cd /shares/<name-of-share>`
* Check the `<user>` owner of the files: `ls -l`
* Get user UID:
```
$ id -u <user>
```
* Get user GID:
```
$ id -g <user>
```
The containers will run impersonated as this user, in order to have read/write access to the media directories.

### Directories
The configuration of all the containers are stored on volumes, mapped with the docker host.

```bash
shares/P2P/tools
├── couchpotato       # Contains CouchPotato configuration, database, cache and logs
│   ├── config.ini    # CouchPotato configuration file (use configurator to initialize, use Web UI for setup)
│   └── ...
├── medusa            # Contains Medusa configuration, database, cache and logs
│   ├── config.ini    # Medusa configuration file (use configurator to setup, use Web UI for full setup)
│   └── ...
├── minidlna          # Contains MiniDLNA database cache (delete content to force reindex)
│   └── ...
├── nginx             # Contains nginx configuration, passwords and logs
│   ├── nginx.conf    # nginx configuration file (use configurator to setup)
│   ├── passwords     # nginx credentials for basic authentication (use configurator to setup)
│   └── logs          # nginx logs
├── resilio           # Contains Resilio configuration files (databases)
├── ssl               # Contains certificates for nginx HTTPS access 
│   └── ...           # **GENERATE FILES .crt AND .key HERE**
└── transmission      # Contains Transmission configuration, cache and logs
    ├── settings.json # Transmission configuration file (do not modify, overwritten by transmission-openvpn)
    └── ...
```

```bash
storage
├── _hd1            # External hard-drive #1
│   ├── Enfants     # Children videos
│   │   ├── Films   # Children movies on HD1, managed by CouchPotato
│   │   ├── Series  # Children TV shows on HD1, managed by Medusa
│   │   └── ...
│   ├── Films       # Movies on HD1, managed by CouchPotato
│   ├── Series      # TV shows on HD1, managed by Medusa
│   └── ...
├── ...
├── complete        # Downloaded torrents by Transmission, published with MiniDLNA
│   ├── couchpotato # Downloaded torrents by Transmission, managed by CouchPotato
│   ├── medusa      # Downloaded torrents by Transmission, managed by Medusa
│   └── seed        # Seeding torrents by Transmission
├── incomplete      # Currently downloading torrents by Transmission
├── watch           # Watch directory for *.torrent files
├── resilio         # Watch directory for *.torrent files
│   ├── downloads   # Resilio downloads directory
│   └── sync        # Resilio sync directory
├── ...
├── Backup          # Old personal photos & videos, published with MiniDLNA
├── Films           # Movies on NAS, managed by CouchPotato and published with MiniDLNA
├── MP3             # Music on NAS, published with MiniDLNA
├── Photos          # Personal photos & videos to publish with MiniDLNA
├── Series          # TV shows on NAS, managed by Medusa and published with MiniDLNA
└── Videos          # Misc videos on NAS, published with MiniDLNA
```
