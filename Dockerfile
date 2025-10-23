FROM python:3.11-slim

# Install Chrome and dependencies (Debian 12+ compatible)
RUN apt-get update && apt-get install -y wget gnupg unzip && \
    mkdir -p /etc/apt/keyrings && \
    wget -q -O /etc/apt/keyrings/google-linux-signing-key.gpg https://dl.google.com/linux/linux_signing_key.pub && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Environment variable for Flask
ENV PORT=8080

# Run Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
