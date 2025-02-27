# APES DEMO
This repo includes code to setup a custom Docker Jupyter Lab notebook for running APES, APES examples, and usign AWS and Google Cloud cli's. 
Our Docker notebook is based on [Docker Jupypter datascience-notebook](https://quay.io/repository/jupyter/datascience-notebook).
The following instructions are to set-up a Google Cloud Workstation to run APES.

## Computer setup
1. Install the [Google cloud CLI tools](https://cloud.google.com/sdk/docs/install) on your work computer.

## Google Cloud worstation setup
1. Create Linux workstation.
2. Use a terminal program and the Google cloud CLI to connect to your workstation via SSH tunnel. The command can be copied from the workstation page. The general form is:
   ```bash
   gcloud workstations ssh --project=PROJECT_NAME --cluster=CLUSTER --config=OS_CONFIG --region=REGION WORKSTATION_NAME
   ```
3. Clone this repo to the workstation.
5. Run the following commands:
   ```bash
    cd AFSC-AASI-APES_GCP 
    chmod +x APES_demo_install.sh 
    ./APES_demo_install.sh
    ```
6. Use the LAUNCH button on the workstation page and password 'APES' to connect to Jupyter Lab.
