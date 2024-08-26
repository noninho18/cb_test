# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get update && apt-get install -y gnupg 

# Creates a non-root user with an explicit UID and adds permission to access the /CB_test folder
RUN adduser --uid 1000 --disabled-password --gecos "" appuser

# Set working directory
WORKDIR /CB_test

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /CB_test
RUN chown -R appuser:appuser /CB_test

# Set permissions and create directory for SSH keys
USER appuser
RUN mkdir -p /home/appuser/.ssh && chmod 700 /home/appuser/.ssh

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python3", "/CB_test/card_check/encrypt_decrypt.py"]