FROM python:3.11
WORKDIR /bot
COPY . /bot

RUN python -m pip install .

ENTRYPOINT [ "python", "-m", "poe2bot.bot" ]