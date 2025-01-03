from flask import Flask, render_template, request
import requests
#flask inicializlasa
app = Flask(__name__)

# TMDB API kulcs 
API_KEY = 'b0ff54d9f03d74a916ff2ecc5fa2ccd0'
BASE_URL = 'https://api.themoviedb.org/3/'

URL = "https://api.themoviedb.org/3/movie/popular"
PARAMS = {
    "api_key": API_KEY,
    "language": "en-US",
}

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
"""
#fooldal route
@app.route('/', methods=['GET'])
def index():
    genres = get_genres()
    selected_genres = request.args.getlist('genre')  # a kivalasztott kategorijak listaja
    return render_template('index.html', genres=genres, selected_genres=selected_genres)
"""

# fooldal route, amely GET es POST metodust is kezel
@app.route('/', methods=['GET', 'POST'])
def index():
    genres = get_genres()  # filmes kategoriak lekerese
    selected_genres = []  # kezdetben ures lista ami a kivalasztott kategoriakat tarolja

    # a felhasznalo rakattintott a sumbit gombra
    if request.method == 'POST':
        selected_ids = request.form.getlist('genre')  # a genre mezok (kivalasztott kategoriak ID-jai)
        
        genre_dict = {str(genre['id']): genre['name'] for genre in genres}
        
        selected_genres = [genre_dict[genre_id] for genre_id in selected_ids if genre_id in genre_dict]

    return render_template('index.html', genres=genres, selected_genres=selected_genres)


# alkalmazas inditasa
if __name__ == '__main__':
    app.run(debug=True)
