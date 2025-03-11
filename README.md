# APES DEMO
This repo includes code to setup a custom Docker Jupyter Lab notebook for running [APES](https://github.com/ElOceanografo/ProbabilisticEchoInversion.jl), [APES examples](https://github.com/ElOceanografo/APESExamples), and using AWS and Google Cloud CLI's. 
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
This repository contains all of the examples provided in [APESExamples](https://github.com/ElOceanografo/APESExamples), with additional notebooks for exploring and demonstrating how APES can be used. Further details are provided in [Urmy et al., 2023](https://doi.org/10.1093/icesjms/fsad102).
- *APESExamples.ipynb*: modified steps for following the APESExamples instructions and running each example provided there.
- *APESExamples/mesopelagic_mix_simulation/mesopelagic_mixture_notebook.ipynb*: annotated notebook of the julia mesopelagic_mixture code (mesopelagic_mixture.jl). This example uses simulated scattering from a mesopelagic mixture to explore the impact of additional priors (video counts, eDNA presence/absence) on acoustic inversion.
- *APESExamples/fish_krill_simulation/fish_krill_notebook.ipynb*: annotated notebook of the julia fish_krill_simulation code (fish_krill_simulation.jl). This example includes acoustic-only inversion of three scenarios representing fish-dominated, krill-dominated, and fish-krill mixture scattering.
- *APESExamples/raw_file* contains three examples of running the [APES library](https://github.com/ElOceanografo/ProbabilisticEchoInversion.jl) directly from Simrad raw files. The example implementation uses the pyEcholab library to read, calibrate, and integrate the raw data into the expected input format, using three different sources of raw data:
   - *raw_file_example_cw.ipynb*: narrowband data, with example .raw file provided
   - *raw_file_example_fm.ipynb*: broadband data, with the user required to upload an example file directly to their workstation
   - *raw_file_example_NCEI.ipynb*: direct download of raw file(s) from the [NCEI AWS S3](https://noaa-wcsd-pds.s3.amazonaws.com/index.html) archival storage
