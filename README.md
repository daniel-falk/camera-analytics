Application for ARMv7 based network camera for door state prediction (door open / door closed).

Idea of project is to create an easy to train installation dependent detector to see if a door is open or closed. Training is done on host (a developer machine) while the prediction is done on edge (in the network camera).

Applications for host written in python (3), applications for camera written in micropython with c-modules for acceleration where needed. Training of neural network is done in pytorch, inference (on edge) shall be done using ulab (numpy-like library for micropython) or a c-module.

A dockerfile for building an SDK or dev env to build c-modules for micropython is included, this handles all cross-compiling for ARMv7.

# TODO:

## Annotation tool

- Add time stamp of annotation
- Step to last annotated frame
- Backup index-file before write
- Create smarter script for sampling training data (motion detection + queue)

## Training

- Fix nice batch-size
- Investigate different network architectures
- Fix feature pruning to reduce compute
