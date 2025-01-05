from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

API_KEY = 'b0ff54d9f03d74a916ff2ecc5fa2ccd0'
BASE_URL = 'https://api.themoviedb.org/3/'

URL = "https://api.themoviedb.org/3/movie/popular"
PARAMS = {
    "api_key": API_KEY,
    "language": "en-US",
}

movies = []
# lekertem a TMDB API ból a filmek mufajait/kategoriajit
def get_genres():
    try:
        url = f"{BASE_URL}genre/movie/list?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        genres = response.json().get('genres', [])
        return genres
    except requests.exceptions.RequestException as e:
        print(f"Error fetching genres: {e}")
        return []

#lekerem a legnepszerubb filmeket TMDB API-ból
def get_popular_movies():
    all_movies = []
    for page in range(1, 5):  # oldalnyi filmet kerek le mivel 1 oldalon 20 darav vab
        PARAMS['page'] = page
        response = requests.get(URL, params=PARAMS)
        if response.status_code == 200:
            data = response.json()
            popular_movies = data.get("results", [])
            all_movies.extend(popular_movies)
        else:
            print(f"Error fetching page {page}: {response.status_code}")
    return all_movies

movies = get_popular_movies()

def filter_movies_by_user_pref(user_pref):
    return [movie for movie in movies if any(genre_id in user_pref for genre_id in movie['genre_ids'])]

 # csak a felhasznalo altal preferalt filmekbol lesznek a kezdeti ertekek 
def population_inicialization(user_pref):
    valid_movies = filter_movies_by_user_pref(user_pref)
    return random.sample(valid_movies, 3) 


def fitness(individual, user_pref):
    score_per_movie = []  # filmek pontszámai

    for movie in individual:
        genre_ids = movie.get("genre_ids", [])  # lekerjuk a film mufajait id-vel

        # a mufaj id kat osszahasonlitom a felhasznalo mufajainak idjaival ha van egyezel novelem 
        match_score = 0
        for genre_id in genre_ids:
            if genre_id in user_pref:
                match_score += 1  # novelem a pontszamot ha van egyezes

        # aa a film rendelkezik legalabb 1 egyezessel (mufajlag) 
        if match_score == len(user_pref):
            score_per_movie.append(match_score )  # Műfaji pontszám összegzése

    return sum(score_per_movie)  # Visszatérünk a teljes pontszámmal


def crossover(parent1, parent2, user_pref):
    # csak azokat a filmeket valasztjuk a szulokbol, amelyek illeszkednek a mufajokhoz
    selected_parent1 = filter_movies_by_user_pref(user_pref)
    selected_parent2 = filter_movies_by_user_pref(user_pref)
    
    # ha nincs ilyen film, akkor a suülok osszes filmjet figyelembe vesszuk
    if not selected_parent1: selected_parent1 = parent1
    if not selected_parent2: selected_parent2 = parent2
    
    split = random.randint(1, min(len(selected_parent1), len(selected_parent2)) - 1)
    return selected_parent1[:split] + selected_parent2[split:]

def mutate(individual, user_pref):
    mutation_point = random.randint(0, len(individual) - 1)
    # valasztunk egy veletlen filmet, ami illeszkedik a mufaj preferenciakhoz
    valid_movies = filter_movies_by_user_pref(user_pref)
    individual[mutation_point] = random.choice(valid_movies)
    return individual


def genetic_algorithm(population_size, generations, user_pref):
    # Az első generáció filmes populációját úgy hozzuk létre, hogy minden film illeszkedjen a felhasználó műfaji preferenciáihoz
    population = [population_inicialization(user_pref) for _ in range(population_size)]
 
    for generation in range(generations):
        # Az egész filmszett értékelése, figyelembe véve a műfaji egyezéseket
        population.sort(key=lambda x: fitness(x, user_pref), reverse=True)
        parents = population[:2]
        new_population = []

        for _ in range(population_size // 2):
            child = crossover(parents[0], parents[1], user_pref)
            child = mutate(child, user_pref)
            new_population.append(child)

        population = new_population

    return population[0][:3]



# Route to render index page and handle form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    genres = get_genres()  
    selected_genres = []  
    user_pref = []  
    best_movies = [] 
    error_message = None

    if request.method == 'POST':
        selected_ids = request.form.getlist('genre')  # Műfajok id-jait választják
        genre_dict = {str(genre['id']): genre['name'] for genre in genres}
        selected_genres = [genre_dict[genre_id] for genre_id in selected_ids if genre_id in genre_dict]

        user_pref = [int(genre_id) for genre_id in selected_ids]  # Az id-ket tároljuk a preferenciában
        if not user_pref:
            error_message = "Please select at least one genre."
            return render_template('index.html', genres=genres, error_message=error_message)

        global movies        
        best_movies = genetic_algorithm(population_size=10, generations=20, user_pref=user_pref)
        print(f"Best movies: {best_movies}")

    
    return render_template('index.html', genres=genres, selected_genres=selected_genres, best_movies=best_movies)

if __name__ == '__main__':
    app.run(debug=True)
