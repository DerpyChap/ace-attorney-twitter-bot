FROM jjanzic/docker-python3-opencv

WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt update && \
  apt install libsm6 libxext6 ffmpeg git -y && \
  pip install -U pipenv && \
  pipenv install --deploy --system && \
  python -m spacy download en_core_web_sm && \
  apt remove git -y && \
  apt autoremove -y && apt clean && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf ~/.cache/pip/*

COPY main.py main.py
COPY ./reddit_bot ./reddit_bot

CMD ["python", "-u", "./main.py"]
