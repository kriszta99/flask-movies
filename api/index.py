from flask import Flask, render_template
import requests

# Flask alkalmazás inicializálása
app = Flask(__name__)
# TMDB API kulcs
BASE_URL = 'https://api.themoviedb.org/3/'

# Funkció a legnépszerűbb filmek lekérésére a TMDB API-ról
def get_popular_movies():
    url = f"{BASE_URL}movie/popular?api_key={b0ff54d9f03d74a916ff2ecc5fa2ccd0}&language=en-US&page=1"
    response = requests.get(url)
    return response.json()['results']

# Főoldal route, ahol megjelenítjük a népszerű filmeket
@app.route('/')
def index():
    # Filmek lekérése
    movies = get_popular_movies()
    return render_template('index.html', movies=movies)

# Alkalmazás indítása
if __name__ == '__main__':
    app.run(debug=True)
