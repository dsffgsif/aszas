FROM python:3.10-slim

# نصب ابزارهای مورد نیاز: ffmpeg، نودجی‌اس و گیت
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نصب و کامپایل ابزار رسمی تولید توکن یوتیوب
RUN git clone --depth=1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil && \
    cd /opt/bgutil/server && \
    npm install && \
    npm run build

# نصب کتابخانه‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# ساخت اسکریپت استارت برای اجرای همزمان سرور توکن و ربات
RUN printf '#!/bin/bash\nnode /opt/bgutil/server/build/main.js --port 4416 &\nsleep 3\nexec python bot.py\n' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
