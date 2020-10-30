#Start from Debian slim
FROM debian:10-slim
#Set Activation code
ENV ACTIVATION Code
#Update apt, install packages needed, purge cache
RUN apt-get update && apt-get dist-upgrade -y && \
    apt-get install ca-certificates python3 iproute2 python3-pip \
    -y --no-install-recommends --no-cache-dir && rm -rf /var/lib/apt/lists/* \
    && pip3 install pexpect==4.8.0
#copy the junk in
COPY contents .
#Install VPN, remove the deb
RUN dpkg -i /expressvpn_3.1.0.34-1_amd64.deb && rm /*.deb
#Healthcheck sees if the expressvpn is connected
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=2 CMD ["/bin/bash", "/health.sh"]
#Start the VPN by running the monitor script
ENTRYPOINT ["python3", "/exprvpnmon.py"]
