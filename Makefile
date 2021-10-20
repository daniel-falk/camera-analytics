CAM ?= cam
CAM_USER ?= root
IMAGE_NAME ?= camera-analytics
IMAGE_TAG ?= latest

build-sdk-base:
	docker build . --target=base -t ${IMAGE_NAME}:base ${BUILD_OPTS}

build-sdk:
	docker build . -t ${IMAGE_NAME}:${IMAGE_TAG} ${BUILD_OPTS}

install-mpy: build-sdk
	tools/install-mpy.sh ${IMAGE_NAME}:${IMAGE_TAG} ${CAM_USER}@${CAM}

run-host-mpy: build-sdk
	docker run --rm -it -v `pwd`:/src/camera-analytics -w /src/camera-analytics ${IMAGE_NAME}:${IMAGE_TAG} /usr/bin/micropython

run-mpy:
	ssh -t ${CAM_USER}@${CAM} LD_LIBRARY_PATH=/tmp/libs /tmp/micropython
