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
    libc6


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

WORKDIR /
RUN make clean
RUN make BLADERF=no RTLSDR=yes
# Create a directory for shared volume
RUN mkdir -p /data

RUN cp /usr/local/lib/librtlsdr.so.0 /

# Expose port for incoming connections
EXPOSE 30002

# CMD instruction to start dump1090 with specified options
CMD ["./dump1090", "--interactive", "--net", "--net-ro-port", "30002"]
