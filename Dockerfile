FROM python:3.11
WORKDIR /bot
COPY . /bot

# Install dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

RUN python -m pip install .

ENTRYPOINT [ "python", "-m", "poe2bot.bot" ]