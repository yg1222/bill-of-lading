# Base image for the build stage
FROM python:3.8-slim-buster AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y wkhtmltopdf

# Install wkhtmltopdf dependencies
RUN apt-get install -y \
    libfontconfig1 \
    libxrender1 \
    wget \
    && rm -rf /var/lib/apt/lists/*




# Move wkhtmltopdf binary to /app/bin directory
#RUN mkdir -p /app/bin && \
    mv /usr/local/bin/wkhtmltopdf /app/bin/ && \
    chmod +x /app/bin/wkhtmltopdf

# Set PATH environment variable to include /app/bin directory
ENV PATH="/app/bin:${PATH}"


# Copy the source code into the container
COPY . /app

# Set the working directory for subsequent commands
WORKDIR /app

# Install dependencies required for building the application
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly setting path for flask
ENV PATH="/app/bin:${PATH}"

# Confirming flask is in the right dir
WORKDIR /app
COPY . .
RUN ls -al

RUN pip list



# Build the application
#RUN python setup.py build

# Second stage of the Dockerfile
FROM python:3.8-slim-buster

# Copy the built application from the builder stage
COPY --from=builder /app /app

# Set the working directory for subsequent commands
WORKDIR /app

RUN pip install flask
RUN pip install pdfkit
RUN chmod +x /*

# Run the application
#CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["flask", "run", "--host=0.0.0.0"]





