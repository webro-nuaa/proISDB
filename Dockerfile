ARG USE_CHINA_MIRROR=false

FROM python:3.11-slim

ARG USE_CHINA_MIRROR

RUN if [ "$USE_CHINA_MIRROR" = "true" ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true; \
    fi

RUN apt-get update && apt-get install -y --no-install-recommends \
    ncbi-blast+ \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN if [ "$USE_CHINA_MIRROR" = "true" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple; \
    fi \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs blast_db

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 5500

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "-c", "deploy/gunicorn.conf.py", "run:app"]
