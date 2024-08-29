# Retell AI Python Backend

This repository contains a production-level FastAPI server that acts as a backend for handling webhooks and creating web calls using the Retell API.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Frontend Integration](#frontend-integration)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/retell-ai-python-backend.git
    cd retell-ai-python-backend
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

3. Create a virtual environment:
    ```sh
    poetry shell
    ```

## Configuration

1. Copy the example environment file and update it with your settings:
    ```sh
    cp .env.example .env
    ```

2. Edit the `.env` file to include your Retell API key and other necessary configurations.

## Running the Server

To run the FastAPI server in development mode:
```
python -m src.agent.api.main
```


## License

This project is licensed under the MIT License.
