# Base image for the build stage
FROM python:3.8-slim-buster AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Install dependencies required for building the application
RUN pip install --upgrade pip 

# Explicitly setting path for flask
ENV PATH="/app/bin:${PATH}"

RUN pip list

RUN if [ ! -d /session ]; then mkdir -p /session; fi

RUN pwd
RUN ls
RUN mkdir logos
RUN ls -ld
RUN chmod 755 /logos
#RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder . /app
COPY . /app

# Set the working directory for subsequent commands
WORKDIR /app
RUN echo "IN APP DIR"
RUN ls

# Run app
#CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "wsgi", ":","app"]