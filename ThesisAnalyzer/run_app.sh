#!/bin/bash
echo "Activating the environment!"
~/miniconda/bin/conda init
echo "Running server..."
~/miniconda/bin/conda run -n thesis-env-3.6 gunicorn ThesisAnalyzer.wsgi:app