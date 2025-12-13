#Imports
import requests, openpyxl, pandas, json
from pathlib import Path


# Global
CONFIG_FILE = "config.json"


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
        
def get_player_id(config: dict, player: dict) -> str:
    # Isolate key and url from config
    key = {"X-Riot-Token": config["riot_api"]["riot_api_key"]}
    riot_url = config["riot_api"]["riot_api_url"]

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




def main():
    # Load config file
    config = load_config()
    print("Config loaded")

    # Get players data from config and check them
    players = config.get("players", [])
    check_players_data(players)

    # Get players technical ID from riot API
    for player in players:
        player["puuid"] = get_player_id(config, player)
    print(players)

# Run
if __name__ == "__main__":
    main()