from flask import Flask, render_template
import requests

# Flask alkalmazás inicializálása
app = Flask(__name__)

# TMDB API kulcs (cseréld ki a saját kulcsodra)
API_KEY = 'b0ff54d9f03d74a916ff2ecc5fa2ccd0'
BASE_URL = 'https://api.themoviedb.org/3/'

# Funkció a legnépszerűbb filmek lekérésére a TMDB API-ról
def get_popular_movies():
    try:
        url = f"{BASE_URL}movie/popular?api_key={API_KEY}&language=en-US&page=1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies: {e}")
        return []


# Főoldal route
@app.route('/')
def index():
    movies = get_popular_movies()
    return render_template('index.html', movies=movies)

# Alkalmazás indítása
if __name__ == '__main__':
    app.run(debug=True)
