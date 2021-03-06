CAM ?= cam
IMAGE_NAME ?= camera-analytics
IMAGE_TAG ?= latest

build-sdk-base:
	docker build . --target=base -t ${IMAGE_NAME}:base ${BUILD_OPTS}

build-sdk:
	docker build . -t ${IMAGE_NAME}:${IMAGE_TAG} ${BUILD_OPTS}

install-mpy: build-sdk
	tools/install-mpy.sh ${IMAGE_NAME}:${IMAGE_TAG} ${CAM}

run-mpy: build-sdk
	docker run --rm -it -v `pwd`:/src/camera-analytics -w /src/camera-analytics ${IMAGE_NAME}:${IMAGE_TAG} /usr/bin/micropython
