CAM ?= cam
SDK_TAG ?= camera-analytics:latest

build-sdk:
	docker build . -t ${SDK_TAG}

install-mpy: build-sdk
	tools/install-mpy.sh ${SDK_TAG} ${CAM}
