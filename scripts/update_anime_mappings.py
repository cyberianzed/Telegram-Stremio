import urllib.request
import os

def update_mappings():
    target_path = os.path.join(os.path.dirname(__file__), "..", "Backend", "helper", "mappings.min.json")
    target_path = os.path.abspath(target_path)
    url = "https://github.com/anibridge/anibridge-mappings/releases/download/v3/mappings.min.json"
    
    print(f"Downloading latest AniBridge mappings to {target_path}...")
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            with open(target_path, "wb") as f:
                f.write(response.read())
        print("AniBridge mappings updated successfully!")
    except Exception as e:
        print(f"Failed to update mappings: {e}")

if __name__ == "__main__":
    update_mappings()
