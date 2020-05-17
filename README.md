Application for ARMv7 based network camera for door state prediction (door open / door closed) using a conv net.

Idea of project is to create an easy to train installation dependent detector to see if a door is open or closed. Training is done on host (a developer machine) while the prediction is done on edge (in the network camera).

Applications for host written in python3.7+, applications for camera written in micropython with c-modules for acceleration where needed. Training of neural network is done in pytorch, inference (on edge) shall be done using ulab (numpy-like library for micropython) or a c-module.

A dockerfile for building an SDK or dev env to build c-modules for micropython is included, this handles all cross-compiling for ARMv7.

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
