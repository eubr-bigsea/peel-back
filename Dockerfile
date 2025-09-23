# Use a slim Python image as the base
FROM python:3.9-slim

LABEL maintainer="Walter Santos <walter@dcc.ufmg.br>, Pedro Henrique <rodrigues.pedro@dcc.ufmg.br>, Lucas Ponce <lucasmsp@dcc.ufmg.br>"

# Set working directory
WORKDIR /peel-back

# Copy just the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set common environment variables
ENV FLASK_ENV=development
ENV FLASK_APP=/peel-back/xai_app.py
ENV TZ=America/Sao_Paulo

# Copy the rest of the application
COPY . .

# Create migrations and .logs folders in a single RUN command
RUN mkdir -p /peel-back/migrations /peel-back/.logs


# Set permissions for the migrations folder
RUN chmod 777 /peel-back/migrations /peel-back/.logs


# Set entrypoint script as executable
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set entrypoint to the script
ENTRYPOINT ["entrypoint.sh"]
