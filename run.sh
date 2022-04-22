#!/bin/sh

if [[ "$(whoami)" == "kristijan" ]]; then
			REPO_DIR=/media/kristijan/kristijan-hdd-ex/general-3d-humans/
			BASE_DATA_DIR=/media/kristijan/kristijan-hdd-ex/datasets/
				else
			REPO_DIR=/home/dbojanic/pose/general-3d-humans/
			BASE_DATA_DIR=/home/dbojanic/datasets/
fi

docker run --rm --gpus all --name kbartol-general-3d-humans -it \
	-v ${REPO_DIR}:/general-3d-humans \
	-v ${BASE_DATA_DIR}/human36m/:/data/human36m/ \
	-v /media/kristijan/kristijan-hdd-ex/panoptic-toolbox/scripts/:/data/cmu/ \
	kbartol-general-3d-humans

