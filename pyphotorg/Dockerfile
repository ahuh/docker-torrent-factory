FROM alpine:3.21

# Env vars (default values)
ENV ENABLE_ORGANIZE=true \
    ENABLE_DEDUPLICATE=true \
    DRY_RUN_MODE=false \
    SCHEDULE_CRON="0 2 * * sun" \
    ORG_TIMESTAMP_TAGS="FileModifyDate,CreationDate,CreateDate,DateTimeOriginal" \
    ORG_STORAGE_PATH_PATTERN="%Y/%Y-%m/%Y%m%d_%H%M%S%%-3c.%%e"

# Install alpine packages
# <!> Install pandas with apk (pip version requires build on arm, too long)
RUN apk add --no-cache bash sudo tini shadow exiftool python3 py3-pandas py3-pip \
    && pip3 install --no-cache-dir --upgrade pip --break-system-packages \
    && ln -sf python3 /usr/bin/python

# Install python packages
RUN pip install --no-cache-dir croniter pause duplicate-finder openpyxl --break-system-packages

# Create and set user & group for impersonation
RUN groupmod -g 1000 users \
    && useradd -u 911 -U -d /userhome -s /bin/false abc \
    && usermod -G users abc

# Copy scripts and make them executable
COPY /scripts/*.sh /scripts/
RUN chmod +x /scripts/*.sh

# Copy Python scripts
COPY /work/*.py /work/

# Entrypoint
ENTRYPOINT ["/sbin/tini", "--"]

# Command
CMD ["/scripts/entrypoint.sh"]