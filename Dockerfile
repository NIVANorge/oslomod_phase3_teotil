FROM python:3.13

WORKDIR /app

RUN apt-get update -qq && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY code/ ./code/
COPY data/ ./data/
COPY README.md ./README.md

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]