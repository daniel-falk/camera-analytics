# Outdated Repo
This repository is mostly outdated. There has been a lot of new thins happening with Edge AI inference and the Axis ACAP SDKs since this repo was created. The repo does however contain a lot of valuable information, therefore I will leave it here as a reference.

For more up to date inforation, take a look at the [AXIS Native SDK](https://github.com/AxisCommunications/acap-native-sdk-examples/) and the [AXIS Computer Vision SDK](https://github.com/AxisCommunications/acap-computer-vision-sdk-examples). You can also read my [comprehensive article on what SDK to use](https://www.linkedin.com/pulse/comprehensive-guide-axis-network-camera-edge-application-sdks/).

# Edge based camera image analytics

This repository aims to be an example for how to build analytics applications for *Axis* network cameras using *micropython*. *micropython* is an extremely low-footprint implementation of the *python* language. The *micropython* interpreter and dependencies can easily be packaged in an *ACAP* (*AXIS Camera Application Platform*) application. This allows for rapid prototyping and fast trial of analytics applications at real sites with no extra hardware. Code written with *micropython* as "glue" can also be easier to maintain, debug and adapt than pure C or C++ code. 

The base in this repository is the pipeline to cross compile *micropython* and to deploy and run it on an *ARMv7* *AXIS* camera (e.g. the *S2L* SoC). The show-case application to perform image analytics using *micropython* is not yet finished, the idea is to do installation specific door state prediction (door open / door closed) using a tiny conv net. The training is done on host (a developer machine) while the prediction should be done completely on edge (in the network camera).

Applications for host are written in *python3.7+* while the applications for the camera are written in *micropython* with c-modules for acceleration where needed. Training of neural networks are done in *pytorch* while the inference (on edge) shall be done using *ulab* (*numpy*-like library for *micropython*) or a c-module utilizing a c inference runtime.

A dockerfile for building an SDK or development environment to build the c-modules for *micropython* is included, this handles all cross-compiling for *ARMv7*.

## Development

### Building and depoying micropython with c modules

First off, clone the repo and checkout all submodules:
```bash
git clone https://github.com/daniel-falk/camera-analytics.git
cd camera-analytics
git submodule update --init
```

To cross compile the *micropython* language together with the c-modules you just need to run the multistage *docker* build process to build the SDK. This can be done with the make target:
```bash
make build-sdk
```

To install the *micropython* language in the camera, use the make target:
```bash
make install-mpy
```

To run the *micropython* interpreter in the camera you can use the *make* target (or *ssh* into the camera manually):
```bash
make run-mpy
```

You can now try e.g. to do a fft analysis in the camera:

```python
>>> import os
>>> os.system("uname -a")
Linux axis-accc******** 4.9.206-axis5 #1 PREEMPT Mon Jun 7 08:54:15 UTC 2021 armv7l GNU/Linux
0
>>>
>>> from ulab import numpy as np
>>> 
>>> np.fft.fft(np.array([1,2,3,4,1,2,3,4]))
(array([20.0, 0.0, -4.0, 0.0, -4.0, 0.0, -4.0, 0.0], dtype=float64), array([0.0, 0.0, 3.999999999999999, 0.0, 0.0, 0.0, -3.999999999999999, 0.0], dtype=float64))
```

You can read JPG images with the [ujpeg library](https://github.com/daniel-falk/ujpeg):
```python
>>> import ujpeg
>>> r, g, b = ujpeg.decode("camera.jpg")
>>> r.shape
(270, 270)
```

### Debuging cross compilation
The c modules are built in the second stage of the multi stage docker build. If this does not work, e.g. when developing the c modules one can build a "base" image where micropython and c modules are not yet compiled. One can then start a container and mount the submodule code from host.
```bash
docker build . --target=base -t camera-analytics:base
docker run --rm -it -v `pwd`/submodules/:/submodules camera-analytics:base
make
```
This mounts the "live version" of the source code and allows for fast iteration if the make command fails, simply fix the code and rerun make.

### Using valgrind to find memory leaks
The SDK and base image includes valgrind which can be used to find memory leaks in e.g. the c modules:
```bash
make build-sdk
docker run --rm -it camera-analytics:latest
valgrind --tool=memcheck --leak-check=full /usr/bin/micropython /submodules/ujpeg/test.py
```

# TODO:

## Data collection

The data is very skewed, if we sample only based on time the door will be closed in the absolute majority of images. We need to base out sampling on clever image analytics so we get as diverse dataset as possible.

- Algorithms for automatic data collection:
    * time based sampling
    * histogram of gradients based sampling
    * histogram of color based sampling
    * sampling based on unexpected detector classification (e.g. door open/closed for very short duration)

## Annotation tool

- Add time stamp of annotation
- Step to last annotated frame
- Backup index-file before write
- Create smarter script for sampling training data (motion detection + queue)

## Training

Currently the fastai based training code gives good performance, train.py is not yet practical.

One idea is to fine tune a large network (e.g. resnet18) and then use is as a teacher network to teach a network that is small enough to run in the camera CPU without noticable load.

- Investigate different network architectures
- Fix feature pruning to reduce compute
