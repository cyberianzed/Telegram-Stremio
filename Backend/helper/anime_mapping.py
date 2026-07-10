import os
import json
from typing import Optional, Tuple
from Backend.logger import LOGGER

MAPPINGS_FILE = os.path.join(os.path.dirname(__file__), "mappings.min.json")
_mappings_data = None

def load_mapping() -> dict:
    global _mappings_data
    if _mappings_data is not None:
        return _mappings_data
    
    if os.path.exists(MAPPINGS_FILE):
        try:
            with open(MAPPINGS_FILE, "r", encoding="utf-8") as f:
                _mappings_data = json.load(f)
            LOGGER.info("AniBridge mappings loaded successfully from local file.")
            return _mappings_data
        except Exception as e:
            LOGGER.error(f"Failed to load local AniBridge mappings: {e}")
    else:
        LOGGER.warning(f"AniBridge mappings file not found at {MAPPINGS_FILE}. Please run scripts/update_anime_mappings.py manually.")
        
    _mappings_data = {}
    return _mappings_data

def parse_range_str(r_str: str) -> Tuple[int, Optional[int]]:
    r_str = r_str.strip()
    if "-" not in r_str:
        try:
            val = int(r_str)
            return val, val
        except ValueError:
            return 0, 0
            
    parts = r_str.split("-")
    try:
        start = int(parts[0])
    except ValueError:
        start = 0
        
    if len(parts) > 1 and parts[1].strip():
        try:
            end = int(parts[1])
        except ValueError:
            end = None
    else:
        end = None
        
    return start, end

def _map_provider(title: str, absolute_episode: int, provider: str, anilist_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
    # Fallback/default logic for One Piece
    if not anilist_id:
        if title.lower() == "one piece":
            anilist_id = 21
        else:
            return None
            
    data = load_mapping()
    ani_key = f"anilist:{anilist_id}"
    if ani_key not in data:
        return None
        
    ani_mappings = data[ani_key]
    prefix = f"{provider}:"
    for key, range_map in ani_mappings.items():
        if not key.startswith(prefix):
            continue
            
        parts = key.split(":")
        if len(parts) < 3 or not parts[-1].startswith("s"):
            continue
            
        try:
            season = int(parts[-1][1:])
        except ValueError:
            continue
            
        for src_range, tgt_range in range_map.items():
            src_start, src_end = parse_range_str(src_range)
            tgt_start, tgt_end = parse_range_str(tgt_range)
            
            if src_start <= absolute_episode and (src_end is None or absolute_episode <= src_end):
                offset = absolute_episode - src_start
                mapped_ep = tgt_start + offset
                return season, mapped_ep
                
    return None

def map_tvdb(title: str, absolute_episode: int, anilist_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
    return _map_provider(title, absolute_episode, "tvdb_show", anilist_id)

def map_tmdb(title: str, absolute_episode: int, anilist_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
    return _map_provider(title, absolute_episode, "tmdb_show", anilist_id)
