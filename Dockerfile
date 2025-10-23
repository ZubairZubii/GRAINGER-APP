FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    fonts-liberation libnss3 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxrandr2 libxss1 libxtst6 libatk1.0-0 libcups2 \
    libdrm2 libdbus-1-3 libgtk-3-0 libasound2 libpangocairo-1.0-0 \
    libatk-bridge2.0-0 libgbm1 libatspi2.0-0 \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O /etc/apt/keyrings/google-linux-signing-key.gpg https://dl.google.com/linux/linux_signing_key.pub \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

ENV PORT=8080
EXPOSE 8080

# Run app with Gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app:app"]
