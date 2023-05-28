# Base image for the build stage
FROM python:3.8-slim-buster AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy the source code into the container
COPY . /app

# Set the working directory for subsequent commands
WORKDIR /app

# Install dependencies required for building the application
RUN pip install --upgrade pip 
# RUN pip install --no-cache-dir -r requirements.txt

# Explicitly setting path for flask
ENV PATH="/app/bin:${PATH}"

# Confirming flask is in the right dir
WORKDIR /app
COPY . .

RUN pip list

RUN if [! -d /session]; then mkdir -p /session; fi

RUN ls

# Build the application
#RUN python setup.py build

# Second stage of the Dockerfile
FROM python:3.8-slim-buster

# Copy the built application from the builder stage
COPY --from=builder /app /app

# Set the working directory for subsequent commands
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
RUN ls
RUN pwd
RUN mkdir logos
RUN ls -ld
RUN chmod u+rw /logos

# Run app
#CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "wsgi", ":","app"]