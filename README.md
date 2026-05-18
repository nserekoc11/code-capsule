# Code Capsule

>A small Python project scaffolded with a launcher and per-project folders.

## Overview

This repository is a lightweight code capsule that collects small apps and projects. It includes a simple launcher script to run or manage contained projects and a few configuration folders.

## Requirements

- Python 3.8+
- (Recommended) a virtual environment

## Quickstart

1. Create and activate a virtual environment (Windows PowerShell):

   ```powershell
   python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt  # if present
   ```

2. Run the launcher:

   ```powershell
   python launcher.py
   ```

If your environment already has a `.venv` directory, activate that instead.

## Project Structure

- `launcher.py` — entry point script to run or manage projects.
- `apps/` — place application code here.
- `configs/` — configuration files shared across apps.
- `projects/` — workspace project folders (e.g. `jun`, `jun1`).
- `workspace/` — user workspace or temporary files.
- `ver_1.txt` — version or notes file.

Adjust paths and names to fit how you organize your apps.

## Contributing

Add issues or pull requests with small, focused changes. Include usage notes for new apps you add under `apps/` or `projects/`.
