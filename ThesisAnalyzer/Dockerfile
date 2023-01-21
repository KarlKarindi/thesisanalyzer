FROM ubuntu:20.04

WORKDIR /usr/src/app

# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;
    
# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# Install base utilities
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y wget \
    && apt-get install -y python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -U setuptools \
    && apt-get clean

# This must be in the correct folder
COPY setup/necessary_files/libcg3.so.1  /usr/lib/x86_64-linux-gnu/

# Install Conda
RUN cd $HOME && wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh && bash Miniconda3-py38_4.10.3-Linux-x86_64.sh -b -p $HOME/miniconda

# Create env
RUN $HOME/miniconda/bin/conda init bash
COPY setup/necessary_files/thesisenv_latest.yml .
RUN $HOME/miniconda/bin/conda env create -f thesisenv_latest.yml
# Activate conda environment on startup
RUN cd $HOME && chmod +x ~/miniconda/bin/conda

CMD ["./ThesisAnalyzer/run_app.sh"]
