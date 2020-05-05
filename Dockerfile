FROM ubuntu:bionic-20200219

# Add foreign architecture so we can apt-get install packages for target
RUN dpkg --add-architecture armhf
RUN sed "s/^deb /deb \[arch=amd64,i386\] /" -i /etc/apt/sources.list
RUN echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports bionic main universe" >> /etc/apt/sources.list
RUN echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports bionic-updates main universe" >> /etc/apt/sources.list
RUN echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports bionic-backports main universe" >> /etc/apt/sources.list
RUN apt-get update

# We need git to clone the tools/code
RUN apt-get install git -y

# Install misc tools on host for building
RUN apt-get install build-essential -y  # We need 'make'
RUN apt-get install autogen -y
RUN apt-get install autoconf -y
RUN apt-get install libtool -y
RUN apt-get install pkg-config -y
RUN apt-get install python3 -y

# Install the cross-compiler toolchain
RUN apt-get install gcc-arm-linux-gnueabihf -y
RUN apt-get install g++-arm-linux-gnueabihf -y
ENV CC=/usr/bin/arm-linux-gnueabihf-gcc
ENV CXX=/usr/bin/arm-linux-gnueabihf-g++
RUN $CC --version
RUN $CXX --version

# We will need libffi headers to cross-compile micropython
RUN apt install libffi-dev:armhf -y
RUN apt install libffi-dev -y

# ujpeg library needs libjpeg installed
RUN apt-get install libjpeg-dev:armhf -y
RUN apt-get install libjpeg-dev -y

# Copy tools scripts
COPY tools/ /tools

WORKDIR /src
RUN git clone https://github.com/micropython/micropython.git
WORKDIR /src/micropython/mpy-cross
RUN make
WORKDIR /src/micropython/ports/unix
RUN make submodules

# Link the c-modules to build with micropython
COPY submodules/ /submodules
ENV USER_C_MODULES=/c_modules/
RUN /tools/add-c-module.sh $USER_C_MODULES /submodules/micropython-ulab/code ULAB
RUN /tools/add-c-module.sh $USER_C_MODULES /submodules/ujpeg/src UJPEG

# Build micropython for host, for testing purpose
RUN make
RUN cp micropython /usr/bin/
RUN make clean

# Cross-compile micropython's unix-port
RUN PKG_CONFIG_PATH=/usr/lib/arm-linux-gnueabihf/pkgconfig/ make deplibs CROSS_COMPILE=arm-linux-gnueabihf-
RUN PKG_CONFIG_PATH=/src/micropython/ports/unix/build-standard/lib/libffi/ make CROSS_COMPILE=arm-linux-gnueabihf-
RUN file micropython
