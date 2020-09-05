# ClothesManager

ClothesManager manages your clothes and closet and suggests the ones that are suitable for the weather.

## Installation

You need [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

Clone this repositry

```
$ git clone https://github.com/yuara/ClothesManager_Flask.git
```

## Run

Change a directory

```
$ cd ClothesManager_Flask
```

Build and up

```
$ docker-compose up -d --build
```

Check logs until this app is completed

```
$ docker-compose logs -f
```

Then access to `http://127.0.0.1:5000/`
