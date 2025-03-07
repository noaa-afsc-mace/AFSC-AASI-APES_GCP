FROM jupyter/datascience-notebook

USER root
RUN apt-get update && apt-get install -y unzip
RUN wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -O awscliv2.zip && unzip awscliv2.zip && ./aws/install

ARG JULIA_VERSION=1.11.3
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_VERSION%.*}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz && tar zxvf julia-${JULIA_VERSION}-linux-x86_64.tar.gz -C /opt && rm -r julia-${JULIA_VERSION}-linux-x86_64.tar.gz && ln -sf /opt/julia-${JULIA_VERSION}/bin/julia /usr/local/bin/julia

USER $NB_UID
WORKDIR /home/$NB_UID

RUN pip install git+https://github.com/leviner/pyEcholab.git && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_UID}"

RUN pip install boto3
RUN pip install lxml
RUN pip install future

RUN wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz && tar -xf google-cloud-cli-linux-x86_64.tar.gz && ./google-cloud-sdk/install.sh -q

ENV PATH=$PATH:/home/$NB_UID/google-cloud-sdk/bin

RUN julia -e 'using Pkg; Pkg.add.(["IJulia","CSV","CategoricalArrays","ColorSchemes","DataFrames","DataFramesMeta","Dierckx","DimensionalData","Distributed","Distributions","ForwardDiff","Glob","ImageFiltering","KernelAbstractions","MAT","Optim","Plots","ProbabilisticEchoInversion","PythonCall","Random","SDWBA","StatsBase","StatsPlots","Turing","UnderwaterAcoustics"]); pkg"precompile"'
