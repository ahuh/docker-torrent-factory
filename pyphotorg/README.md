# Pyphotorg
Docker image hosting a photo / video organizer and deduplicator implemented in Python 3, for ARM / x86 / x64 devices.
* Github link: https://github.com/ahuh/docker-torrent-factory/tree/master/pyphotorg
* Dockerhub link: https://hub.docker.com/r/ahuh/pyphotorg

## Features

Main features :
* **Move and organize photos and videos** from an incoming directory (e.g. sync dir populated with smartphone photos) into a storage directory structure, using metadatas (EXIF) to rename files and create a date-based dir structure. The program ExifTool (https://exiftool.org), embedded in the docker image, is used to implement this feature.
* **Deduplicate photos and videos** in a storage directory structure, to save space and keep a clean photo library. The python module **Duplicate-Finder** (https://github.com/akcarsten/Duplicate-Finder ; https://pypi.org/project/Duplicate-Finder/), embedded in the docker image, is used to implement this feature.
* **Schedule the organize and deduplicate job**, using a customizable cron-like syntax. The python module **Croniter** (https://github.com/taichino/croniter ; https://pypi.org/project/croniter/), embedded in the docker image, is used to implement this feature.

Detailed features for organizer :
* Metadatas are extracted from all photo AND video files using ExifTool (dates and times). These metadatas are used to create a directory structure in storage dir (based on year, month, etc) and to rename the files (using date and time).
* The organizer handles medias with same date and time, and automatically adds a suffix to filename to prevent file overwrite and data loss.
* Multiple pairs of incoming and storage dirs may be configured (e.g. to organize files backed-up from multiple smartphones to different storage folders).
* Multiple ordered date/time metadatas may be selected and used in target storage dirs / filenames : if a photo or video has no value for the 1st metadata, the 2nd metadata is used, etc.
* The target storage dir structure and filename may be customized with a pattern syntax. The default pattern corresponds to the following organisation:

```bash
/storage
└── 2021                             # [Year]
    └── 2021-07                      # [Year]-[Month]
        └── 20210716_175913-001.jpg  # [Year][Month][Day]_[Hour][Min][Sec][-XXX].[ext]
                                     # [-XXX] suffix for files with same date/time
```

Detailed features for deduplicator :
* Duplicate photos and videos are detected with 2 mechanism: firstly, the files with same size are selected, secondly, only file with same hash based on content are marked as duplicates
* An order algorithm is applied to keep only the best file for each duplicate set:
  * 1) Duplicates are deleted in dirs with highest order value before those with lowest order value (duplicates in dirs with no order are deleted first)
  * 2) Duplicates in last dirs in alphabetic path order are deleted first
  * 3) Duplicates with longest filenames are deleted first
* Duplicate files marked for deletion are archived in the backup directory, reproducing the same dir structure as their original location (no automatic deletion)
* After each deduplicate operation, an Excel report is generated in the backup directory (with timestamp in filename) with the list of duplicate files detected, and those marked for removal

Other features :
* All logs are displayed in stdout, available with command `docker logs pyphotorg` (or in Portainer web UI)
* A dry-run mode is available: if enable, no file is moved in organize operation, and no file is removed in deduplicate operation. Instead, simulated actions are logged and the deduplication report is generated.

## Configuration example with docker-compose

```yaml
version: "3.3"

services:
  # ==========================================================================
  # pyphotorg
  pyphotorg:
    image: ahuh/pyphotorg:latest
    container_name: pyphotorg
    environment:
      # Operation switches
      - ENABLE_ORGANIZE=true
      - ENABLE_DEDUPLICATE=true
      # Dry-run mode (no modification applied) or real mode
      - DRY_RUN_MODE=false
      # Job scheduler (cron format)
      - "SCHEDULE_CRON=15 2 * * sun"
      # Deduplicator - Dirs and priority orders for duplicate removal (remove duplicates from highest to lowest number)
      - "DEDUP_STORAGE_PATH=/storage/Photos"
      - "DEDUP_BACKUP_PATH=/storage/Backup/pyphotorg"
      - "DEDUP_DIR_ORDER_01=/storage/Photos/Family"
      - "DEDUP_DIR_ORDER_02=/storage/Photos/Friends"
      - "DEDUP_DIR_ORDER_03=/storage/Photos/Mobile-A"
      - "DEDUP_DIR_ORDER_04=/storage/Photos/Mobile-B"
      - "DEDUP_DIR_PATH_FILTER=/.@__thumb"
      # Organizer - Path couples: sync dirs (source) and storage dirs (target)
      - "ORG_INCOMING_PATH_01=/storage/sync/camera-a"
      - "ORG_STORAGE_PATH_01=/storage/Photos/Mobile-A"
      - "ORG_INCOMING_PATH_02=/storage/sync/camera-b"
      - "ORG_STORAGE_PATH_02=/storage/Photos/Mobile-B"
      # Organizer parameters
      - ORG_TIMESTAMP_TAGS=FileModifyDate,CreationDate,CreateDate,DateTimeOriginal
      - ORG_STORAGE_PATH_PATTERN=%Y/%Y-%m/%Y%m%d_%H%M%S%%-3c.%%e
      # User from docker host to impersonate in container
      - PUID=500
      - PGID=1000
    volumes:
      - /etc/localtime:/etc/localtime:ro
      # Sync dir
      - /share/homes/XXX/.Qsync:/storage/sync
      # Storage dir
      - /share/Perso/Photos:/storage/Photos
      # Backup dir
      - /share/Perso/Backup/pyphotorg:/storage/Backup/pyphotorg
    restart: always
```

## Preparation
Before running container, you have to retrieve UID and GID for the user used to mount your tv shows directory:
* Get user UID:
```
$ id -u <user>
```
* Get user GID:
```
$ id -g <user>
```
The container will run impersonated as this user, in order to have read/write access to volume directories.<br />
<br />
You also need to create volume directories before launching the container with the same user rights.

## Parameters

Env var name     | Default value | Description
-----------------|---------------|------------
ENABLE_ORGANIZE          | `true` | If enable, organize operation is launch at the beginning of each job execution
ENABLE_DEDUPLICATE       | `true` | If enable, deduplicate operation is launch at the end of each job execution
DRY_RUN_MODE             | `false` | In dry-run mode, photo / video files are not modified or move : only reports and logs are generated
SCHEDULE_CRON            | `0 2 * * sun` | Schedule for job execution in format `min hour day_of_month month day_of_week`. See http://en.wikipedia.org/wiki/Cron for details
DEDUP_STORAGE_PATH       | | Storage directory containing photo / videos files to process, during deduplication operation
DEDUP_BACKUP_PATH        | | Backup directory to use, during deduplication operation. Each duplicate file removed is backed-up in this directory (with the same directory structure as the original). An Excel report is alse generated here at each execution (if duplicate files detected)
DEDUP_DIR_ORDER_XX       | | OPTIONAL - Multiple variables supported (XX=01, 02, etc). Directory priority orders for duplicate removal (remove duplicates from highest to lowest number)
DEDUP_DIR_PATH_FILTER    | | OPTIONAL - Directories containing this string are filtered to prevent deduplication. E.g. "/.@__thumb" for QNAP NAS thumbnails generated automatically
ORG_INCOMING_PATH_XX     | | Multiple variables supported (XX=01, 02, etc). List of incoming directory (source) for move / organize operation. Each value is coupled with the corresponding storage directory value (same XX index). If no variable used: the storage dir is used as source and target ('in-place' organize)
ORG_STORAGE_PATH_XX      | | Multiple variables supported (XX=01, 02, etc). List of storage directory (target) for move / organize operation. Each value is coupled with the corresponding incoming directory value (same XX index)
ORG_TIMESTAMP_TAGS       | `FileModifyDate,CreationDate,`<br />`CreateDate,DateTimeOriginal` | List of metadata to use in reverse order of priority for path / filename insertion, during move / organize operation. See documentation here: https://exiftool.org/filename.html#ex12
ORG_STORAGE_PATH_PATTERN | `%Y/%Y-%m/%Y%m%d_`<br />`%H%M%S%%-3c.%%e` | Relative path to target dir (base path = ORG_STORAGE_PATH_XX) and target filenames, during organize operation. See documentation here: https://exiftool.org/filename.html#codes
PUID                     | | User UID to use for job impersonation
PGID                     | | User GID to use for job impersonation

## HOW-TOs

### Manual execution
In addition to the scheduled jobs, each operation may be launched manually. These commands are available in docker container using `docker exec -ti pyphotorg bash` (or in Portainer web UI)
* Manual organizer:
  ```
  $ ./scripts/execPy.sh /work/manual_organize.py -h
  ```
* Manual deduplicator:
  ```
  $ ./scripts/execPy.sh /work/manual_deduplicate.py -h
  ```
Each script has a command-line help available with arg `-h`, explaining how to set parameters.

You may also execute the scheduled job manually:
```
$ ./scripts/execPy.sh /work/manual_job.py
```

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