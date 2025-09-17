-----

# PersonaQuant - Backend

This repository contains the backend code for **PersonaQuant**, a multi-agent AI system. 🤖

-----

## Development Setup

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python** (version 3.8 or higher is recommended)
  * **uv** (a fast Python package manager)

If you don't have `uv`, you can install it with `pip`:

```bash
pip install uv
```

-----

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/udaymehta/personaquant_backend.git
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd reponame
    ```

3.  **Install dependencies:**
    This command will create a virtual environment and install all the required packages specified in `pyproject.toml`.

    ```bash
    uv sync
    ```

-----

## Running the Server

Once the installation is complete, you can start the backend server using the following command:

```bash
uv run main.py
```

The server should now be running, and you'll see output logs in your terminal. ✨
