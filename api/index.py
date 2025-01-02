from flask import Flask, render_template, request
import requests
#flask inicializlasa
app = Flask(__name__)

# TMDB API kulcs 
API_KEY = 'b0ff54d9f03d74a916ff2ecc5fa2ccd0'
BASE_URL = 'https://api.themoviedb.org/3/'

# filmes kategoriak lekerdezese a TMDB API-rol
def get_genres():
    try:
        url = f"{BASE_URL}genre/movie/list?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        genres = response.json().get('genres', [])
        print(f"Genres: {genres}")
        return genres
    except requests.exceptions.RequestException as e:
        print(f"Error fetching genres: {e}")
        return []

#fooldal route
@app.route('/', methods=['GET'])
def index():
    genres = get_genres()
    selected_genres = request.args.getlist('genre')  # a kivalasztott kategorijak listaja
    return render_template('index.html', genres=genres, selected_genres=selected_genres)


# alkalmazas inditasa
if __name__ == '__main__':
    app.run(debug=True)
