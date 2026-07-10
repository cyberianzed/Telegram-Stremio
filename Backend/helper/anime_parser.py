import re
from typing import Optional
from Backend.helper.pyro import clean_filename
from Backend.helper.metadata import parse_media_name

_QUALITY_PATTERNS = [
    (r"\b2160p\b|\b4k\b", "2160p"),
    (r"\b1440p\b|\b2k\b", "1440p"),
    (r"\b1080p\b|\bfhd\b", "1080p"),
    (r"\b720p\b|\bhd\b", "720p"),
    (r"\b480p\b|\bsd\b", "480p"),
    (r"\b360p\b", "360p")
]

def extract_quality_single(text: str) -> str:
    if not text:
        return ""
    text_lower = text.lower()
    for pattern, label in _QUALITY_PATTERNS:
        if re.search(pattern, text_lower):
            return label
    return ""

def extract_quality(filename: str, caption: str) -> str:
    # 1. Try filename quality
    q = extract_quality_single(filename)
    if q:
        return q
    # 2. Try caption quality
    q = extract_quality_single(caption)
    if q:
        return q
    # 3. Default to 720p for anime channels
    return "720p"

def extract_absolute_episode_single(text: str) -> Optional[int]:
    if not text:
        return None
    
    # Normalize separators (underscores, dots, dashes) to spaces for clean boundaries
    normalized = re.sub(r"[._-]+", " ", text)
    
    # 1. Look for explicit episode markers (ep, episode, e, etc.)
    for pattern in [
        r"\b(?:ep|episode|e|eps|sp)\.?\s*(\d+)\b",
        r"\b(\d+)\s*(?:ep|episode|e|eps)\b"
    ]:
        matches = re.findall(pattern, normalized, re.IGNORECASE)
        if matches:
            return int(matches[0])
            
    # 2. Look for standalone numbers, excluding standard resolutions and common years
    candidates = re.findall(r"\b(\d{1,4})\b", normalized)
    for cand in candidates:
        val = int(cand)
        if val in (1080, 2160, 1440, 720, 480, 360, 240):
            continue
        if 1990 <= val <= 2030:
            continue
        return val
        
    return None

def extract_absolute_episode(filename: str, caption: str) -> Optional[int]:
    # Prefer filename, then caption
    ep = extract_absolute_episode_single(clean_filename(filename))
    if ep is not None:
        return ep
    return extract_absolute_episode_single(clean_filename(caption))

def extract_anime_title(filename: str, caption: str) -> str:
    combined = f"{filename} {caption}".lower()
    if "one piece" in combined:
        return "One Piece"
        
    parsed_fn = parse_media_name(clean_filename(filename))
    if parsed_fn.get("title"):
        return parsed_fn["title"]
    parsed_cap = parse_media_name(clean_filename(caption))
    return parsed_cap.get("title") or ""

def parse_anime_message(filename: str, caption: str) -> dict:
    cleaned_fn = clean_filename(filename) if filename else ""
    cleaned_cap = clean_filename(caption) if caption else ""
    
    parsed_fn = parse_media_name(cleaned_fn)
    parsed_cap = parse_media_name(cleaned_cap)
    
    title = extract_anime_title(filename, caption)
    abs_ep = extract_absolute_episode(filename, caption)
    quality = extract_quality(filename, caption)
    year = parsed_fn.get("year") or parsed_cap.get("year")
    
    return {
        "title": title,
        "absolute_episode": abs_ep,
        "quality": quality,
        "year": year
    }
