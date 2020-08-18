# ClothesManager

ClothesManager manages your clothes and closet and suggests the ones that are suitable for the weather.

## Installation

You need [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

Clone this repositry

```
$ git clone https://github.com/yuara/ClothesManager.git
```

## Run

Change [Change Here] in .env.sample for you and the file name to .env.dev.

Then build and up the docker-compose

```
$ docker-compose up -d --build
```

Access to `http://127.0.0.1:5000/`
