# APES DEMO
This repo includes code to setup a custom Docker Jupyter Lab notebook for running [APES](https://github.com/ElOceanografo/ProbabilisticEchoInversion.jl), [APES examples](https://github.com/ElOceanografo/APESExamples), and usign AWS and Google Cloud CLI's. 
Our Docker notebook is based on [Docker Jupypter datascience-notebook](https://quay.io/repository/jupyter/datascience-notebook).
The following instructions are to set-up a Google Cloud Workstation to run APES.

## Computer setup
1. Install the [Google cloud CLI tools](https://cloud.google.com/sdk/docs/install) on your computer.

## Google Cloud workstation setup
1. Create and start a Linux workstation in your Google Cloud project.
2. Use a terminal program and the Google Cloud CLI to connect to your workstation via SSH tunnel. The command can be copied using the drop-down menu next to the LAUNCH button for your workstation (Selec 'Connect using SSH...' and copy from pop-up box). The general form is:
   ```bash
   gcloud workstations ssh --project=PROJECT_NAME --cluster=CLUSTER --config=OS_CONFIG --region=REGION WORKSTATION_NAME
   ```
3. Clone this repo to the workstation.
4. Run the APES_demo_install script following commands:
   ```bash
    cd AFSC-AASI-APES_GCP 
    chmod +x APES_demo_install.sh 
    ./APES_demo_install.sh
    ```
   This script will install Docker, build the custom Docker datascience notebook container for running APES, and lauch the container.
5. Use the LAUNCH button on the workstation page and password 'APES' to connect to Jupyter Lab.

## APES Examples
We have included different notebooks for exploring and demonstrating how APES can be used. 
- APESExamples.ipynb: modified steps for following the [APESExamples](https://github.com/ElOceanografo/APESExamples) instructions and running each example provided there.
- APESExamples/raw_file/raw_file_example.ipynb: steps for processing raw echogram data using the [APES package](https://github.com/ElOceanografo/ProbabilisticEchoInversion.jl)
- APESExamples/mesopelagic_mix_simulation/mesopelagic_mixture.ipynb: annotated notebook of the julia mesopelagic_mixture code (mesopelagic_mixture.jl)
