# RAG

This is a prototype of the implementation of the RAG model for question answering.

## Requiremnets

- Python 3.8 or later

## Install Python unsing Conda

1) download and install Conda from [https://repo.anaconda.com/archive/](I downloaded Anaconda3-2025.06-0-Linux-x86_64.sh )

2) Create a environment using this command : 
```bash
$ conda create -n rag-app python=3.8
```

3) Activate the envirment using this command : 
```bach
$ conda activate rag-app
```
## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. 

## Run Docker Compose services

```bash
$ cd docker
$ cp .env.example .env
```

-update '.env' with your credentials

```bash
$ cd docker
$ cd docker compose up -d
```



## Run the FastAPI server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```