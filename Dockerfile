FROM python:3.9.18-bookworm

RUN apt-get update

RUN groupadd -r bot \
  && useradd -g bot -r -m bot

USER bot

WORKDIR /app

COPY --chown=bot:bot  ./requirements.txt .

COPY --chown=bot:bot  . .

RUN pip install -r requirements.txt