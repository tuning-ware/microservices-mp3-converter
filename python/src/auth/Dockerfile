FROM python:3.10-slim-bullseye

# install os dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential default-libmysqlclient-dev pkg-config \
  && pip install --cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
# rebuild the run layer (with new requirements installed) and subsequent layers if requirements.txt changes
RUN pip install --no-cache-dir --requirement /app/requirements.txt
# seperate copying the app directory and requirements.txt on 2 different layers. RUN layer is the most time consuming
COPY . /app
# dot mean the current directory we ran the docker build command in
# Docker will detect changes in the working directory and rebuild the layer

EXPOSE 5000

CMD ["python3", "server.py"]
