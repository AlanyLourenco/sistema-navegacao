FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb \
        x11vnc \
        novnc \
        libx11-6 libxext6 libxrender1 libxrandr2 libxi6 \
        xclip \
        fontconfig fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements antes do código para aproveitar cache do Docker
COPY ["versao Python/requirements.txt", "/tmp/requirements.txt"]
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir websockify

COPY ["versao Python/", "/app/"]
COPY Campus2UFG* /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 6080
ENV PYTHONUNBUFFERED=1

CMD ["/entrypoint.sh"]
