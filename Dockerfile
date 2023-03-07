# Base image for the build stage
FROM python:3.8-slim-buster AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y wkhtmltopdf

# Copy the source code into the container
COPY . /app

# Set the working directory for subsequent commands
WORKDIR /app

# Install dependencies required for building the application
RUN pip install --upgrade pip && pip install -r requirements.txt

# Build the application
#RUN python setup.py build

# Second stage of the Dockerfile
FROM python:3.8-slim-buster

# Copy the built application from the builder stage
COPY --from=builder /app /app

# Set the working directory for subsequent commands
WORKDIR /app

# Run the application
CMD ["flask", "run"]





