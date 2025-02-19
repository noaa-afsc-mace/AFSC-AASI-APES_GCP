#!/bin/bash
#
# Script for launching custom Docker jupyter notebook with APES examples
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
	rm install.sh	
fi

home_dir="$HOME"
repo_dir="AFSC-AASI-APES_GCP"

if [ -d "$home_dir/$repo_dir" ]; then
	echo "AFSC-AASI-APES_GCP already cloned"	
#	return
else
	cd $home_dir
	git clone git@github.com:noaa-afsc-mace/AFSC-AASI-APES_GCP.git
fi

cd AFSC-AASI-APES_GCP
docker build -t jupyter-apes .

cd $home_dir

docker run -it --rm -v "$PWD":/home/jovyan/AFSC-AASI-APES_GCP -w /home/jovyan/AFSC-AASI-APES_GCP -p 80:8888 jupyter-apes start-notebook.py --ServerApp.allow_origin='*'  --IdentityProvider.token='APES'
