# Use an official Python runtime as a parent image
FROM python:3.10.13-slim@sha256:1d517e04d033a04d86f7de57bf41cae166ca362b37a1cb229e326bc1d754db55 as base

FROM base as builder

# Install any system-level dependencies
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget g++ \
    && rm -rf /var/lib/apt/lists/*

# # Set the working directory in the container for the builder stage
# WORKDIR /orderlogservice_builder

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container for the application
WORKDIR /log_server

# Grab packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/ /usr/local/lib/python3.10/

# Copy the application code
COPY . .

# Set the listen port
ENV PORT "03138"
EXPOSE 03138

# Define the entry point for the container
CMD ["python", "server.py"]