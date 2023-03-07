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


# Download wkhtmltopdf binary
RUN wget -q https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox-0.12.6_linux-generic-amd64.tar.xz

# Extract and move wkhtmltopdf binary to /usr/local/bin
RUN tar xf wkhtmltox-0.12.6_linux-generic-amd64.tar.xz && \
    mv wkhtmltox/bin/wkhtmltopdf /usr/local/bin && \
    rm -rf wkhtmltox




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
RUN chmod +x /

# Run the application
#CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["flask", "run", "--host=0.0.0.0"]





