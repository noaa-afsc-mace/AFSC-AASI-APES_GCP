FROM jupyter/datascience-notebook

USER root
RUN apt-get update && apt-get install -y unzip
RUN wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -O awscliv2.zip && unzip awscliv2.zip && ./aws/install

USER $NB_UID
WORKDIR /home/$NB_UID

RUN pip install git+https://github.com/leviner/pyEcholab.git && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_UID}"

RUN pip install lxml
RUN pip install future

RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.11/julia-1.11.3-linux-x86_64.tar.gz && tar zxvf julia-1.11.3-linux-x86_64.tar.gz
ENV PATH=$PATH:/home/$NB_UID/julia-1.11.3/bin

RUN julia -e 'using Pkg; pkg"add IJulia"; pkg"precompile"'

# Alt version:
#RUN julia -e 'using Pkg; Pkg.add.(["CSV", "DataFrames", "DataFramesMeta", "Plots","Glob","DimensionalData","ProbabilisticEchoInversion","Distributed","SDWBA","UnderwaterAcoustics","PythonCall","IJulia"]); pkg"precompile"'
