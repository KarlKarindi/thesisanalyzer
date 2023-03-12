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
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/conda \
    && rm miniconda.sh

ENV PATH="/opt/conda/bin:$PATH"

# Create env
COPY setup/necessary_files/thesisenv_latest.yml .
RUN conda --version
RUN conda env create -f thesisenv_latest.yml

# Start the app with Gunicorn
CMD ["conda", "run", "-n", "thesis-env-3.6", "gunicorn", "ThesisAnalyzer.wsgi:app", "--name", "thesisanalyzer", "--workers", "4", "--timeout", "900"]
