#!/bin/bash
#
# Script for launching  Docker jupyter notebook with APES examples
#

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

if command_exists docker; then
	echo "Docker already installed"
#       return
else
	wget https://github.com/docker/docker-install/blob/master/install.sh
	chmod +x install.sh
 	source ./install.sh	
fi

docker pull quay.io/jupyter/julia-notebook:julia-1.9.3

home_dir="$HOME"
repo_dir="AFSC-AASI-APES_GCP"

if [ -d "$home_dir/$repo_dir" ]; then
	echo "AFSC-AASI-APES_GCP already cloned"	
#	return
else
	cd $home_dir
	git clone git@github.com:noaa-afsc-mace/AFSC-AASI-APES_GCP.git
fi

docker run -it --rm -v "$PWD":/home/jovyan/AFSC-AASI-APES_GCP -w /home/jovyan/AFSC-AASI-APES_GCP -p 80:8888 quay.io/jupyter/julia-notebook-1.9.3 start-notebook.py --ServerApp.allow_origin='*'
