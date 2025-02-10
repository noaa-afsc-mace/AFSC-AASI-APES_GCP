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

docker pull quay.io/jupyter/julia-notebook

home_dir="$HOME"
repo_dir="APESExamples"

if [ -d "$home_dir/$repo_dir" ]; then
	echo "APESExamples already cloned"	
#	return
else
	cd $home_dir
	git clone https://github.com/ElOceanografo/APESExamples.git
fi

docker run -it --rm -v "$PWD":/home/jovyan/APESExample -w /home/jovyan/APESExample -p 80:8888 quay.io/jupyter/julia-notebook
