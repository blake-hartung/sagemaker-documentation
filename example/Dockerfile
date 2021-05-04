# Python 3.7 Tensorflow GPU Enabled Container Image
FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/tensorflow-training:2.4.1-gpu-py37-cu110-ubuntu18.04

ENV PATH="/opt/ml/code:${PATH}"

# Run Pip install ... or use a requirements.txt for necessary libraries (outside of Tf)
RUN pip --no-cache-dir install pandas==1.2.4 numpy==1.19.5 scikit-learn==0.24.1

# Required call telling SageMaker the main directory
ENV SAGEMAKER_SUBMIT_DIRECTORY /opt/ml/code

# This directory is used to tell our training program the place to save output files to
ENV SM_MODEL_DIR /opt/ml/model 

# This directory points your training script to the data that will be copied into the container
ENV SM_CHANNEL_TRAINING /opt/ml/input/data/training

# This copies the training script from the current directory into the container image
COPY intent_training.py /opt/ml/code/intent_training.py

# Required call telling sagemaker the main program
ENV SAGEMAKER_PROGRAM intent_training.py

# Exec format ENTRYPOINT tells SageMaker the file we want to enter into
ENTRYPOINT ["python", "/opt/ml/code/intent_training.py"]