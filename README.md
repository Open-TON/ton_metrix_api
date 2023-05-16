# Metrix - The Main data extractor & API provider service

The service implements background workers to load data and the server app exposing API endpoints.  

## Set-up config
```bash
cd <path-to-the-repo>
cp config.ini.template config.ini
```

open `config.ini` and set the parameters.

## Set-up requirements
```bash
cd <path-to-the-repo>
pip install poetry==1.4.1
poetry install --no-root
```

## Running API Server
```bash
export PYTHONPATH=<path-to-the-repo>
uvicorn --reload --factory --host=0.0.0.0 --port=8000 src.main:app_factory
```

## Running workers
### Redis filler

To prefetch price data run:
```bash
cd <path-to-the-repo>/src
PYTHONPATH=<path-to-the-repo> python redis_filler.py
cd <path-to-the-repo>
arq src.redis_filler.InitializationSettings
```

then run Scheduler:
```bash
arq src.schedule_exec.WorkerSettings
```
