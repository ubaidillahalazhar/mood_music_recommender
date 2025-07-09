import os
import json
import requests
import random
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from the .env file (within backend/ folder)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Determine paths for Flask to serve frontend files
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.join(backend_dir, os.pardir)
frontend_dir = os.path.join(project_root_dir, 'frontend')

app = Flask(__name__,
            static_folder=os.path.join(frontend_dir, 'static'),
            template_folder=frontend_dir)

# --- API Keys & Base URLs ---
ZENQUOTES_ALL_QUOTES_URL = "https://zenquotes.io/api/quotes"
ZENQUOTES_RANDOM_URL = "https://zenquotes.io/api/random"

# Path to data file (within backend/data/)
DATA_FILE = os.path.join(backend_dir, 'data', 'favorites.json')


def load_data():
    """Loads data from a JSON file. Returns an empty structure if the file does not exist or is corrupted."""
    if not os.path.exists(DATA_FILE):
        return {"history": [], "favorites": []}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {DATA_FILE}. Returning empty data.")
        return {"history": [], "favorites": []}
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return {"history": [], "favorites": []}

def save_data(data):
    """Saves data to a JSON file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An error occurred while saving data to {DATA_FILE}: {e}")


def get_dummy_recommendations(mood):
    """Provides dummy music recommendations based on mood."""
    dummy_songs = {
        'happy': [
            {"title": "Love Story", "artist": "Taylor Swift", "url": "https://youtu.be/8xg3vE8Ie_E?si=ANah2S5dxLuntc8T"}, 
            {"title": "Cantik", "artist": "Tiara Andini & Arsy Widianto", "url": "https://youtu.be/QMpbUCoW65M?si=312tnWqd8E0_8dFb"}, 
            {"title": "Siapkah Kau 'Tuk Jatuh Cinta Lagi", "artist": "Hivi!", "url": "https://youtu.be/kX1O93X77d4?si=Da6cSiNYIjsDlmU8"}, 
            {"title": "Steal My Girl", "artist": "One Direction", "url": "https://youtu.be/UpsKGvPjAgw?si=VumKk_E06oDxAzig"}, 
            {"title": "The Lazy Song", "artist": "Bruno Mars", "url": "https://youtu.be/fLexgOxsZu0?si=dFDtGr_bTt8FlNhh"}, 
            {"title": "Shake It Off", "artist": "Taylor Swift", "url": "https://youtu.be/nfWlot6h_JM?si=o5Q2ULus2ELpdfxt"}, 
          
        ],
        'sad': [
            {"title": "Selamat (Selamat Tinggal)", "artist": "Virgoun & Audy", "url": "https://youtu.be/ZPxqSAHonSs?si=NTE7iwD-FykGzBAV"},
            {"title": "Someone Like You", "artist": "Adele", "url": "https://youtu.be/hLQl3WQQoQ0?si=jSqfhFvUP8Nchc-v"}, 
            {"title": "Happier", "artist": "Olivia Rodrigo", "url": "https://www.youtube.com/watch?v=Kz7GzFw310U"}, 
            {"title": "We Can't be Friend", "artist": "Ariana Grande", "url": "https://youtu.be/KNtJGQkC-WI?si=WHYHp1k5GPgKWNcv"}, 
            {"title": "No Body Gets Me", "artist": "SZA", "url": "https://youtu.be/tOTr9CCutiE?si=Dovqgl6YgmtC8gqm"}, 
            {"title": "Night Changes", "artist": "One Direction", "url": "https://youtu.be/syFZfO_wfMQ?si=Tw3Oqk0slnl3Bu9m"}, 
            
        ],
        'chill': [
            {"title": "Supoerhero", "artist": "Lauv", "url": "https://youtu.be/Z2dE90tjU6s?si=aVpEiYPXrcY7nH3e"}, 
            {"title": "Weightless", "artist": "Marconi Union", "url": "https://youtu.be/UfcAVejslrU?si=OKD58ADg1tdWt-zO"}, 
            {"title": "Come Away With Me", "artist": "Norah Jones", "url": "https://youtu.be/lbjZPFBD6JU?si=FPBb-C1IKBgQBc_q"}, 
            {"title": "Island In The Sun", "artist": "Weezer", "url": "https://youtu.be/erG5rgNYSdk?si=ZEf8cicB0L5piPEP"}, 
            {"title": "Sunday Morning", "artist": "Maroon 5", "url": "https://youtu.be/S2Cti12XBw4?si=osnIeNWTYroyQ5Wi"},
            {"title": "What A Wonderful World", "artist": "Louis Armstrong", "url": "https://youtu.be/rBrd_3VMC3c?si=C7zbanhcOLFkN7Ak"}, 
            
        ],
        'angry': [
            {"title": "The Way I Loved You", "artist": "Taylor Swift", "url": "https://youtu.be/DlexmDDSDZ0?si=LFKp4b3-QJRA2oVx"}, 
            {"title": "No Body, No Crime (feat. HAIM)", "artist": "Taylor Swift ft. HAIM", "url": "https://youtu.be/IEPomqor2A8?si=vQTu43Ap-xx0aLVq"}, 
            {"title": "Good 4 U", "artist": "Olivia Rodrigo", "url": "https://youtu.be/gNi_6U5Pm_o?si=v1-z_ZgZhQwH6-Pr"}, 
            {"title": "I hate You", "artist": "SZA", "url": "https://youtu.be/O04nsyB8gqA?si=Q-kcke5bfwjfpYrS"}, 
            {"title": "Payphone", "artist": "Maroon 5 ft. Wiz Khalifa", "url": "https://youtu.be/KRaWnd3LJfs?si=i6IpJpjZV4dNtaxT"}, 
            {"title": "That Sould be Me", "artist": "Justin Bieber", "url": "https://youtu.be/_pBq1lz1Riw?si=JQhDH9aai4o9APP8"}, 
           
       ],
        'romantic': [   
            {"title": "Paper Rings", "artist": "Taylor Swift", "url": "https://youtu.be/8zdg-pDF10g?si=HhtjPK2HRgjFnipo"}, 
            {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "url": "https://youtu.be/kPa7bsKwL-c?si=gHIzXgRqFktNtqkG"},
            {"title": "I Love You 3000", "artist": "Stephanie Poetri", "url": "https://youtu.be/cPkE0IbDVs4?si=FeZqQKC4r0Usb3FL"}, 
            {"title": "Perfect", "artist": "Ed Sheeran", "url": "https://youtu.be/2Vv-BfVoq4g?si=qJrEa5Hqp-WYZNtk"}, 
            {"title": "cardigan", "artist": "Taylor Swift", "url": "https://youtu.be/K-a8s8OLBSE?si=J7KEKXm2R4U2BmNh"}, 
            {"title": "A Thousand Years", "artist": "Christina Putri", "url": "https://youtu.be/rtOvBOTyX00?si=lVg1dJMp_20RCWMN"}, 
        ]
    }
    return dummy_songs.get(mood.lower(), []) # Return empty list if mood not found

def get_multiple_zen_quotes(count):
    """Fetches multiple random quotes from ZenQuotes.io."""
    quotes = []
    try:
        # ZenQuotes /quotes endpoint returns up to 50 quotes at once
        response = requests.get(ZENQUOTES_ALL_QUOTES_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for item in data:
            quote = item.get('q', 'No quote found.')
            author = item.get('a', 'Unknown')
            quotes.append(f'"{quote}" - {author}')
        
        # If we need more than what /quotes provides (max 50), or if /quotes fails,
        # we can fall back to calling /random multiple times.
        # This loop also helps to get more unique quotes if /quotes returns duplicates
        while len(quotes) < count:
            try:
                rand_response = requests.get(ZENQUOTES_RANDOM_URL, timeout=5)
                rand_response.raise_for_status()
                rand_data = rand_response.json()
                if rand_data and isinstance(rand_data, list) and len(rand_data) > 0:
                    quote = rand_data[0].get('q', 'No quote found.')
                    author = rand_data[0].get('a', 'Unknown')
                    quotes.append(f'"{quote}" - {author}')
            except requests.exceptions.RequestException as e:
                print(f"Error fetching individual random ZenQuote: {e}")
                break # Stop trying if single random call fails
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all ZenQuotes data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with ZenQuotes API: {e}")
    
    # Ensure we have at least 'count' quotes, even if they are duplicates or default
    while len(quotes) < count:
        quotes.append("The only way to do great work is to love what you do.")
        
    return quotes

# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main frontend HTML file."""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_music():
    """Handles music recommendation requests based on mood."""
    mood = request.json.get('mood')
    if not mood:
        return jsonify({"error": "Mood not provided"}), 400

    songs = get_dummy_recommendations(mood)
    
    # Get enough unique quotes for all songs
    # We request more than needed to ensure uniqueness if random returns duplicates
    num_songs = len(songs)
    # Request twice the number of songs to increase chances of unique quotes
    all_quotes = get_multiple_zen_quotes(num_songs * 2) 
    
    # Use a set to keep track of used quotes to ensure uniqueness per request
    used_quotes = set()
    unique_quotes_for_session = []

    # Try to pick unique quotes
    for q in all_quotes:
        if q not in used_quotes:
            unique_quotes_for_session.append(q)
            used_quotes.add(q)
        if len(unique_quotes_for_session) >= num_songs:
            break
    
    # If not enough unique quotes, fill with what we have (might be duplicates)
    while len(unique_quotes_for_session) < num_songs:
        # Fallback to random choice from available quotes if unique ones run out
        unique_quotes_for_session.append(random.choice(all_quotes) if all_quotes else "The only way to do great work is to love what you do.")

    # Shuffle the unique quotes to randomize their assignment to songs
    random.shuffle(unique_quotes_for_session)

    recommended_items = []
    for i, song in enumerate(songs):
        item = song.copy()
        # Assign a unique quote from the pre-fetched list
        # Use modulo operator to cycle through quotes if there are fewer unique quotes than songs
        item['quote'] = unique_quotes_for_session[i % len(unique_quotes_for_session)] 
        recommended_items.append(item)

    # Save history
    data = load_data()
    data['history'].append({
        "mood": mood,
        "timestamp": request.json.get('timestamp'),
        "recommendations": recommended_items
    })
    save_data(data)

    return jsonify({"songs": recommended_items})

@app.route('/favorites')
def get_favorites():
    """Returns the list of favorite songs."""
    data = load_data()
    return jsonify({"favorites": data.get('favorites', [])})

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    """Adds a song to the favorites list."""
    favorite_data = request.json
    if not favorite_data:
        return jsonify({"error": "Favorite data not provided"}), 400

    data = load_data()
    # Check if the song already exists in favorites to avoid duplicates based on URL
    if not any(f.get('url') == favorite_data.get('url') for f in data['favorites']):
        data['favorites'].append(favorite_data)
        save_data(data)
        return jsonify({"message": "Song added to favorites"}), 200
    else:
        return jsonify({"message": "Song already in favorites"}), 200

@app.route('/delete_favorite', methods=['POST'])
def delete_favorite():
    """Deletes a song from the favorites list."""
    song_url = request.json.get('url') # Use generic 'url' for deletion
    if not song_url:
        return jsonify({"error": "Song URL not provided"}), 400

    data = load_data()
    initial_count = len(data['favorites'])
    data['favorites'] = [f for f in data['favorites'] if f.get('url') != song_url]
    
    if len(data['favorites']) < initial_count:
        save_data(data)
        return jsonify({"message": "Song removed from favorites"}), 200
    else:
        return jsonify({"message": "Song not found in favorites"}), 404


if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs(os.path.join(backend_dir, 'data'), exist_ok=True)
    # Run Flask on port 5000, accessible from any IP
    app.run(debug=True, host='0.0.0.0', port=5000)

