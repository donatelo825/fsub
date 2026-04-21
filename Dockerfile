FROM python:3.11-slim

WORKDIR /app

# Install git (dibutuhkan pip untuk install pyrogram dari GitHub)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENV_FILE=.env

CMD ["sh", "-c", "ENV_FILE=${ENV_FILE} python main.py"]
