# api_data_reporter
A lightweight Python script that fetches data from a public API and generates structured Excel reports.

In this specific implementation, the script retrieves daily League of Legends match data from the Riot Games API for personal analysis and reporting.

---

## Context
Given configuration data for the Riot Games API and one or more player identifiers (game name and tag line)
<img width="435" height="347" alt="image" src="https://github.com/user-attachments/assets/aa25fdd6-f739-49e1-90f7-0f84936805e4" />

The aim of this project is to :
* Retrieve games played the last 24 hours for each configured player
* Extract relevant player-centric data into pandas dataframes
* Generate `.xlsx` report - one report / player
<img width="484" height="142" alt="image" src="https://github.com/user-attachments/assets/59812b88-1ea5-4983-bac6-673fd346961d" />

* Be designed to run as a systemd service

---

## Script description :

* `reporter.py` - main script responsible for API calls, data processing and report generation
* `config.json` - runtime configuration and user-defined parameters (API credentials, players, output path)

---

## How to run it

To use the script locally, clone the repository using the `git clone` command, then set up a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Once done, configure the application:
* Rename `config.json.empty` to `config.json`
* Fill the file with your own parameters (riot API key, player game name and tag line, output directory)

You can then test the script with:
```bash
python reporter.py
```

After execution, one Excel report per player will be generated in the configured output directory.

You should now have everything needed to run the script on a local computer.
If you want to learn how to deploy it on an Ubuntu server using systemd, feel free to contact me directly (see GitMews on GitHub).
