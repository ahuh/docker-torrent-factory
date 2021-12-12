FROM alpine:3.14.0

# Volumes
VOLUME /config

# Install packages
RUN apk add --no-cache bash curl jq tini tar shadow apache2-utils py3-pip \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir crudini

# Download latest release of JOAL with config files
RUN mkdir -p /tmp/joal \
 	&& export JOAL_VERSION=$(curl -k -sX GET "https://api.github.com/repos/anthonyraymond/joal-desktop/releases/latest" | jq -r .tag_name) \
	&& curl -k -o /tmp/joal.tar.gz -sSL "https://github.com/anthonyraymond/joal/releases/download/${JOAL_VERSION}/joal.tar.gz" \
	&& tar xvfz /tmp/joal.tar.gz -C /tmp/joal \
    && rm -rf /tmp/joal/*.* \
    && rm -rf /tmp/joal/torrents

# Create and set user & group for impersonation
RUN groupmod -g 1000 users \
    && useradd -u 911 -U -d /userhome -s /bin/false abc \
    && usermod -G users abc

# Copy resources and scripts
COPY /resources/*.* /resources/
COPY /scripts/*.sh /scripts/
RUN chmod +x /scripts/*.sh

# Entrypoint
ENTRYPOINT ["/sbin/tini", "--"]

# Command
CMD ["/scripts/entrypoint.sh"]