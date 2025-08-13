
BASE = "https://bitmidi.com"
API_SEARCH = BASE + "/api/midi/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": BASE
}

def clean_filename(name, artist):
    """Remove artist name, special characters, and ensure proper .mid extension."""
    # Remove artist name (case-insensitive) with optional separators
    name = name.strip()
    artist_variants = [artist, artist.lower(), artist.upper(), artist.title()]
    for variant in artist_variants:
        # Remove artist name with separators like -, _, or spaces
        pattern = r'\b' + re.escape(variant) + r'\s*[-_\s]*'
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    # Remove special characters, keep alphanumeric, spaces, and hyphens
    name = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace multiple spaces or hyphens with a single underscore
    name = re.sub(r'[\s-]+', '_', name)
    # Remove illegal filename characters
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    # Ensure the name is not empty and add .mid extension
    return (name if name else "Unknown_Song") + ".mid"

def fetch_page(artist, page=0):
    params = {"q": artist, "page": page}
    try:
        resp = requests.get(API_SEARCH, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json().get("result")
    except Exception as e:
        print(f"[ERROR] Failed to fetch page {page} for '{artist}': {e}")
        return None

def download_mid(result, folder, song_list_file, artist):
    dl = result.get("downloadUrl")
    name = result.get("name", "Unknown Song").strip()
    if not dl:
        return
    
    # Clean file name for saving
    safe_name = clean_filename(name, artist)
    file_path = os.path.join(folder, safe_name)

    # Save original song name to list
    with open(song_list_file, "a", encoding="utf-8") as f:
        f.write(name + "\n")

    if os.path.exists(file_path):
        print(f"[SKIP] {file_path} already exists")
        return
    try:
        url = BASE + dl
        r = requests.get(url, stream=True, headers=HEADERS, timeout=15)
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"[DOWNLOADED] {name} -> {file_path}")
    except Exception as e:
        print(f"[FAIL] Couldn't download {url}: {e}")

def scrape(artist):
    base_folder = "Artists"
    safe = artist.replace(" ", "_")
    artist_folder = os.path.join(base_folder, safe)  # Download inside Artists/ArtistName
    os.makedirs(artist_folder, exist_ok=True)
    song_list_file = os.path.join(artist_folder, f"{safe}_songs.txt")

    # Clear old list
    if os.path.exists(song_list_file):
        os.remove(song_list_file)

    page = 0
    while True:
        print(f"Fetching page {page} for '{artist}'...")
        data = fetch_page(artist, page)
        if not data or not data.get("results"):
            print(f"[DONE] No more results for '{artist}'.")
            break

        for item in data["results"]:
            download_mid(item, artist_folder, song_list_file, artist)

        time.sleep(1)  # polite delay
        page += 1
        if page >= data.get("pageTotal", page + 1):
            break

        time.sleep(2)


if __name__ == "__main__":
    artists_file = "artist.json"
    try:
        with open(artists_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            artists = data.get("artists", [])
    except Exception as e:
        print(f"[ERROR] Failed to read artists file '{artists_file}': {e}")
        sys.exit(1)
    
    if not artists:
        print("No artists found in the file.")
        sys.exit(1)
    
    # Iterate through all artists from the file
    for artist in artists:
        print(f"\nProcessing artist: {artist}")
        scrape(artist)