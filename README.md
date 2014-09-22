# Test task

## Installation

```sh
pip3 install PyYAML
pip3 install Django
cmd/syncdb
cmd/makemigrations main
cmd/migrate
```

## Usage

### After editing DB schema ([models.yaml](./main/models.yaml))

```sh
cmd/makemigrations
cmd/migrate
```

### Start server

```sh
cmd/runserver
```

## Demo

[testtask-testtask.rhcloud.com](http://testtask-testtask.rhcloud.com/)
