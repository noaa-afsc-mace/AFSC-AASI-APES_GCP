FROM jupyter/datascience-notebook

USER root
RUN apt-get update && apt-get install -y unzip
RUN wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -O awscliv2.zip && unzip awscliv2.zip && ./aws/install

USER $NB_UID
WORKDIR /home/$NB_UID

RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.11/julia-1.11.3-linux-x86_64.tar.gz && tar zxvf julia-1.11.3-linux-x86_64.tar.gz
ENV PATH=$PATH:/home/$NB_UID/julia-1.11.3/bin

RUN julia -e 'using Pkg; pkg"add IJulia"; pkg"precompile"'

ENV PYTHONPATH=/home/jovyan/AFSC-AASI-APES_GCP/pyEcholab
