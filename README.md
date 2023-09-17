# [Backend] Test task

## Task description

Implement 3 microservices:

1. Sensor: produces HTTP requests to controller at 300 RPS with some integer payload and timestamp,
   have 8 instances running simultaneously.
2. Controller: analyzes sensor data and based on it every 5 seconds sends command to the manipulator
   via TCP sockets. Allows to get command history in given period.
3. Manipulator: just accepts commands and logs them.

More details about the task available [here](https://disk.yandex.ru/i/kjqK0SedfDFiZQ).

## How to run

### The whole project

Tested with Docker version 20.10.23+dfsg1 and Docker Compose version v2.2.3.

1. Copy `.env.example` to `.env` and change it if needed:
    ```shell
    cp .env.example .env
    ```

2. Build docker images and run the project:
    ```shell
    docker compose up --build
    ```

### Tests

Python 3.11 is required to run the tests.

1. Install requirements:
    ```shell
    pip install -r ./src/tests/requirements.txt -r ./controller/requirements.txt
    ```
2. Run tests:
    ```shell
    pytest ./src/tests
    ```
3. (Optional) check coverage:
    ```shell
    pytest --cov=controller ./src/tests
    ```

## Implementation details

### Sensor

Have two main components based on async `while True` loop:

1. Data generator: produces random payloads at given rate (300 per second by default) and puts them
   to the job queue. Prints actual rate using `tqdm` by default, useful for tuning sleep interval.
2. Worker: takes payloads from queue and sends them using `aiohttp`.

Sensor has a worker pool of a fixed size (16 by default).

### Manipulator

Simple synchronous TCP server created using `soketserver` standard library.

### Controller

Simple `FastAPI` server. Uses Mongo DB for storing sensor data and command history. Have a
background async loop with decision algorithm.

#### Decision algorithm

For each period calculates mean and standard deviation, changes manipulator status if mean is
significantly (checked using t-test with 0.05 level of significance) different from the previous
period.

#### History

`/history` endpoint returns data in the following format:

```javascript
[
    {
        "from_datetime": "datetime in ISO 8601 format",
        "to_datetime": "datetime in ISO 8601 format",
        "status": "up" | "down"
    }
]
```