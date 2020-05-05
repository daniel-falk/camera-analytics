CAM ?= cam
SDK_TAG ?= camera-analytics:latest

build-sdk:
	docker build . -t ${SDK_TAG} ${BUILD_OPTS}

install-mpy: build-sdk
	tools/install-mpy.sh ${SDK_TAG} ${CAM}

run-mpy: build-sdk
	docker run --rm -it -v `pwd`:/src/camera-analytics -w /src/camera-analytics ${SDK_TAG} /usr/bin/micropython
