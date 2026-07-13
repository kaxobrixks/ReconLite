# ReconLite
Lightweight Python OSINT reconnaissance framework for domain analysis, username discovery, reporting, and extensible plugin-based workflows.



## Setup & Installation

### Requirements

* Python **3.7+**
* pip (included with most Python installations)

Check your Python version:

```bash
python --version
```

or:

```bash
python3 --version
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/reconlite.git
cd reconlite
```

Or download the repository as a ZIP file and extract it.

---

### 2. Create a virtual environment (recommended)

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

ReconLite works without third-party dependencies using Python's standard library.

For enhanced features, install optional dependencies:

```bash
pip install -r requirements.txt
```

Or install individual optional packages:

```bash
pip install dnspython pyyaml tqdm
```

Optional packages provide:

* `dnspython` — advanced DNS record resolution
* `pyyaml` — YAML configuration support
* `tqdm` — progress indicators

---

## Verify Installation

Run:

```bash
python main.py --version
```

Expected output:

```
ReconLite v1.1.0
```

View available commands:

```bash
python main.py --help
```

---

## First Run

### Domain reconnaissance

Test DNS reconnaissance:

```bash
python main.py --domain example.com
```

Results will be saved automatically:

```
reports/
├── recon_YYYYMMDD_HHMMSS.json
└── recon_YYYYMMDD_HHMMSS.md
```

---

### Username reconnaissance

Check username availability:

```bash
python main.py --username targetuser
```

ReconLite will check configured platforms and generate a report.

---

## Configuration

ReconLite automatically loads configuration from:

### Windows

```
%APPDATA%/reconlite/config.yaml
```

### Linux/macOS

```
~/.config/reconlite/config.yaml
```

### Project directory

```
./config/config.yaml
```

A default configuration template is available:

```
config/default.yaml
```

---

## Running as a CLI Tool

Common commands:

```bash
# Domain scan
python main.py --domain example.com

# Username scan
python main.py --username username

# View latest report
python main.py --report latest

# List available plugins
python main.py --list-plugins
```

---

## Development Setup

Install development dependencies:

```bash
pip install -r requirements.txt
```

Run tests or verify functionality:

```bash
python main.py --help
```

---

## Updating

Pull the latest changes:

```bash
git pull
```

Update dependencies:

```bash
pip install -r requirements.txt --upgrade
```
