FROM python:3.11

RUN apt update && apt install tzdata -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
ENV TZ="Asia/Ho_Chi_Minh"

# Workdir with non-root user
WORKDIR /app
RUN chown -R nobody:nogroup /app && chmod 755 /app
USER nobody
COPY --chown=nobody:nogroup app/. .
COPY --chown=nobody:nogroup requirements.txt .

USER root
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install -r requirements.txt
RUN apt install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev libreoffice
