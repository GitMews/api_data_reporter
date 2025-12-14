#Imports
import requests, openpyxl, pandas, json
from pathlib import Path
from datetime import datetime, timedelta, date
import pandas as pd
import logging


# Setup
CONFIG_FILE = "config.json"
logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler("reporter.log", encoding="utf-8"),logging.StreamHandler()])


# Functions
def load_config() -> dict:
    # Config file must be valid JSON file
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {CONFIG_FILE}")
    
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in config file: {e}")
    
def check_players_data(players: list):
    # Players must be dictonaries with game_name and tag_line properties
    for player in players:
        if not isinstance(player, dict):
            raise ValueError("Each player must be a dictionary")

        if "game_name" not in player or "tag_line" not in player:
            raise ValueError("Player must define 'game_name' and 'tag_line'")
        
def get_player_puuid(key: str, riot_url:str, player: dict) -> str:
    # Isolate player name and tag
    game_name = player["game_name"]
    tag_line = player["tag_line"]

    # Build request_url
    request_url = f"{riot_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

    # Try to call API
    try:
        response = requests.get(request_url, headers=key, timeout=10)

    except requests.RequestException as e:
        raise RuntimeError(f"Request failed for {game_name}#{tag_line}: {e}")

    # Check response status
    if response.status_code != 200:
        raise RuntimeError(f"API error for {game_name}#{tag_line}: " f"{response.status_code} - {response.text}")

    # Return player puuid if everything is ok
    return response.json()["puuid"]

def get_player_games_ids(key: str, riot_url:str, player: dict) -> list:
    # Isolate player name, tag and puuid
    game_name = player["game_name"]
    tag_line = player["tag_line"]
    puuid = player["puuid"]

    # Build request_url
    start_time = int((datetime.now() - timedelta(days=1)).timestamp())
    request_url = f"{riot_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start_time}&queue=420"

    # Try to call API
    try:
        response = requests.get(request_url, headers=key, timeout=10)
    
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed for {game_name}#{tag_line}: {e}")
    
    # Check response status
    if response.status_code != 200:
        raise RuntimeError(f"API error for {game_name}#{tag_line}: " f"{response.status_code} - {response.text}")
    
    # Return player games list if everything is ok
    return response.json()
    
def get_game_data(key: dict, riot_url: str, game_id: str) -> dict:
    # Build request URL
    request_url = f"{riot_url}/lol/match/v5/matches/{game_id}"

    # Try to call API
    try:
        response = requests.get(request_url, headers=key, timeout=10)

    except requests.RequestException as e:
        raise RuntimeError(f"Request failed for game {game_id}: {e}")

    # Check response status
    if response.status_code != 200:
        raise RuntimeError(f"API error for game {game_id}: "f"{response.status_code} - {response.text}")

    # Return game data if everything is ok
    return response.json()

def build_dataframe(games: list, player_puuid: str) -> pd.DataFrame:
    # Initialize relevant games data - games data are will be dict
    data = []

    # Get data for each game
    for game in games:
        relevant_data = extract_relevant_data_from_game(game, player_puuid)
        data.append(relevant_data)
    
    return pd.DataFrame(data)

def extract_relevant_data_from_game(game: dict, player_puuid: str) -> dict:
    # Initialize game_data
    relevant_data = {}

    # Get player data
    players_data = game["info"]["participants"]
    for data in players_data:
        if data["puuid"] == player_puuid:
            player_data = data
            break

    # Get result
    if player_data["win"]:
        relevant_data["Result"] = "WIN"
    else:
        relevant_data["Result"] = "LOSS"

    # Get champion
    relevant_data["Champion"] = player_data["championName"]

    # Get lane
    relevant_data["Lane"] = player_data["lane"]

    # Get K/D/A
    relevant_data["Kills"] = player_data["kills"]
    relevant_data["Deaths"] = player_data["deaths"]
    relevant_data["Assists"] = player_data["assists"]

    # Get duration
    raw_duration = game["info"]["gameDuration"]
    relevant_data["Duration"] = f"{raw_duration // 60}:{raw_duration % 60:02d}"
    
    return relevant_data


def main():
    # Get logger
    logger = logging.getLogger(__name__)

    # Load config file
    config = load_config()
    logger.info("Config loaded")

    # Get key and url from config
    key = {"X-Riot-Token": config["riot_api"]["riot_api_key"]}
    riot_url = config["riot_api"]["riot_api_url"]

    # Get players data from config and check them
    players = config.get("players", [])
    check_players_data(players)

    # Get players technical ID from riot API
    for player in players:
        player["puuid"] = get_player_puuid(key, riot_url, player)
    logger.info("Player(s) ID(s) acquired")

    # Get games ID for each player
    for player in players:
        player["games_ids"] = get_player_games_ids(key, riot_url, player)
    logger.info("Game(s) IDs acquired")

    # Get games data
    for player in players:
        player["games"] = []
        for game_id in player["games_ids"]:
            player["games"].append(get_game_data(key, riot_url, game_id))
    logger.info("Game(s) data acquired")

    # Build dataframes
    for player in players :
        games = player["games"]
        dataframe = build_dataframe(games, player["puuid"])
        player["dataframe"] = dataframe
    logger.info("Dataframe(s) built")

    # Generate excel reports
    today = date.today().isoformat()
    for player in players :
        player_name = player["game_name"]
        filename = f"report_{player_name}_{today}.xlsx"
        output_path = Path(config["reports_directory_path"]) / filename
        player["dataframe"].to_excel(output_path, index=False)
    logger.info("Excel file(s) generated")

# Run
if __name__ == "__main__":
    main()