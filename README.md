-----

# PersonaQuant - Backend

This repository contains the backend code for **PersonaQuant**, a multi-agent AI system. 🤖

-----

## ⚡ Quick Start

```bash
# Install dependencies
uv sync

# Start server (fast ~6-7s startup!)
uv run python main.py
```

Server will be running at `http://127.0.0.1:8000`

📖 **See [QUICK_START.md](QUICK_START.md) for detailed usage guide**

-----

## 🚀 Performance

- **Startup Time**: ~6-7 seconds (53% faster than before!)
- **Memory Usage**: ~100MB idle, ~1GB after model loading
- **Sentiment Analysis**: <100ms (using pre-computed database)

📊 **See [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) for optimization details**  
📊 **See [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for sentiment system details**

-----

## 📈 Sentiment Analysis System

The sentiment analysis tools now use a **pre-computed database approach** for ultra-fast responses:

### Quick Setup
```bash
# 1. Test system setup
python test_sentiment_system.py

# 2. Collect initial data (5-10 minutes)
python fetch_sentiment_data.py

# 3. Tools now respond in <100ms!
```

### Automated Updates (Recommended)
Run data collection every 12 hours to keep sentiment data fresh:
```bash
# Add to crontab
crontab -e

# Add this line:
0 6,18 * * * /home/um/dev/projects/pqbackend/run_sentiment_fetch.sh >> /home/um/dev/projects/pqbackend/sentiment_fetch.log 2>&1
```

� **See [SENTIMENT_DATA_SETUP.md](SENTIMENT_DATA_SETUP.md) for complete guide**  
📖 **See [CRON_SETUP.md](CRON_SETUP.md) for scheduling options**

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
uvicorn main:app --reload
```

The server should now be running, and you'll see output logs in your terminal. ✨
