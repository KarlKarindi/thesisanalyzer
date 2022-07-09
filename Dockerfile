FROM ubuntu:20.04

WORKDIR /ThesisAnalyzer

# Install base utilities
RUN apt-get update && apt-get install -y build-essential && apt-get install -y wget && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH


COPY /ThesisAnalyzer/setup/necessary_files/thesisenv_latest.yml .
RUN conda env create -f thesisenv_latest.yml

RUN conda activate thesis-env-3.6

RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

