FROM python:3.13-bookworm

WORKDIR /app

COPY . .

ENV UV_HTTP_TIMEOUT=600
ENV DEBIAN_FRONTEND=noninteractive

# Install libreoffice, tesseract-ocr
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-script-provider-python \
        libreoffice-writer \ 
        tesseract-ocr \
        libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install gcloud SDK
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-cli && \
    apt-get clean

# Install Chrome with all required dependencies for headless operation
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    tini \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    ca-certificates \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install requirements and setup
RUN uv pip install --no-cache-dir --system -e .

# Create directory for Chrome user data with proper permissions
RUN mkdir -p /tmp/chrome-user-data && chmod 1777 /tmp/chrome-user-data

# Expose port which is exposed by application to send and receive requests
EXPOSE 8080 

# Use tini as entrypoint to reap zombie processes
ENTRYPOINT ["/usr/bin/tini", "--"]

CMD [ "python", "app.py" ]
