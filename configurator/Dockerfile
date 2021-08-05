FROM alpine:3.14.0

# Volumes
VOLUME /config

# Install packages
RUN apk add --no-cache bash tini shadow apache2-utils py3-pip \
    && pip3 install --no-cache-dir --upgrade pip \
    # Install crudini with pip (not available as alpine pkg), in version 0.9.3 (first version compatible Python3, not yet available in py-pip)
    && pip install --no-cache-dir https://github.com/pixelb/crudini/releases/download/0.9.3/crudini-0.9.3.tar.gz

# Create and set user & group for impersonation
RUN groupmod -g 1000 users \
    && useradd -u 911 -U -d /userhome -s /bin/false abc \
    && usermod -G users abc

# Copy resources
COPY nginx.conf /resources/nginx.conf
COPY entrypoint.sh /scripts/entrypoint.sh
COPY userSetup.sh /scripts/userSetup.sh
RUN chmod +x /scripts/*.sh

# Entrypoint
ENTRYPOINT ["/sbin/tini", "--"]

# Command
CMD ["/scripts/entrypoint.sh"]