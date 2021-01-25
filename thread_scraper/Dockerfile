FROM python:3.9.0-slim-buster
WORKDIR /app

RUN adduser --disabled-password --disabled-login --gecos '' python

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt update && \
  apt install hunspell libhunspell-dev git -y && \
  pip install -U pipenv && \
  pipenv install --deploy --system && \
  python -m spacy download en && \
  apt remove git -y && \
  apt autoremove -y && apt clean && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf ~/.cache/pip/*

RUN chown -R python:python /app
USER python

COPY --chown=python:python main.py main.py

CMD ["python", "-u", "./main.py"]
