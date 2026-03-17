# dump1090 Dockerfile
FROM debian:latest

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    cmake \
    pkg-config \
    libusb-1.0-0-dev \
    git \
    libc6 \
    wget


COPY . .

# Clone RTL-SDR from GitHub
RUN git clone https://github.com/osmocom/rtl-sdr.git \
    && mkdir -p rtl-sdr/build

# Build RTL-SDR
WORKDIR /rtl-sdr/build
RUN cmake ../ -DINSTALL_UDEV_RULES=ON \
    && make \
    && make install
ENV LD_LIBRARY_PATH=/usr/local/lib/

# Add rtl-sdr rules (download directly from github)
RUN wget -O /etc/udev/rules.d/rtl-sdr.rules \
    https://raw.githubusercontent.com/osmocom/rtl-sdr/master/rtl-sdr.rules

# Make sure to blacklist dvb_usb_rtl28xxu on the host:
# echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtl.conf


WORKDIR /
RUN make clean
RUN make BLADERF=no RTLSDR=yes
# Create a directory for shared volume
RUN mkdir -p /data

RUN cp /usr/local/lib/librtlsdr.so.0 /

# Expose port for incoming connections
EXPOSE 30002

# CMD instruction to start dump1090 with specified options
CMD ["sleep", "infinity"]
#CMD ["./dump1090", "--interactive", "--net", "--net-ro-port", "30002"]
#ENTRYPOINT ["/entrypoint.sh"]
