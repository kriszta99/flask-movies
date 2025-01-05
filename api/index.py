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
    for page in range(1, 10):  # oldalnyi filmet kerek le mivel 1 oldalon 20 darav vab
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

def remove_duplicates(movies):
    # az 'id' kulcskent hasznalva 
    movie_dict = {}
    for movie in movies:
        movie_id = movie['id']  # Minden film azonosítójának lekérése
        movie_dict[movie_id] = movie  # A szótárban az azonosítóval tároljuk a filmet
    
    # A szótár értékeit alakítjuk listává
    unique_movies = list(movie_dict.values())
    return unique_movies

def filter_movies_by_user_pref(user_pref):
    return [movie for movie in movies if any(genre_id in user_pref for genre_id in movie['genre_ids'])]

def population_inicialization(user_pref):
    return random.sample(movies, 3) 


def fitness(individual, user_pref):
    # Filmek pontszámainak tárolása
    score_per_movie = []
    for movie in individual:
        genre_ids = movie.get("genre_ids", [])  # A film műfajainak ID-jait szedjük ki
        
        # A felhasználó preferált műfajainak ID-jai
        match_score = 0
        for genre_id in genre_ids:
            if genre_id in user_pref:
                match_score += 1  # Egyezésnél növeljük a pontszámot
        
        # Minden filmhez hozzáadjuk a pontszámot
        score_per_movie.append(match_score)

    # Átlagpontszám kiszámítása az egyedhez (filmszett)
    average_score = sum(score_per_movie) / len(score_per_movie) if score_per_movie else 0

    # Az összes műfaj ID összevetése a felhasználó preferenciáival
    all_genres_in_individual = [genre_id for movie in individual for genre_id in movie.get("genre_ids", [])]
    # Diverzitás bónusz: különböző műfajok egyezése, ami megnöveli a relevanciát
    diversity_bonus = len(set(user_pref) & set(all_genres_in_individual))

    # Súlyozott bónusz: az átlagpontszámhoz hozzáadott diverzitás
    final_score = average_score + (diversity_bonus * 0.5)  # A bónusz súlyozása finomítva

    return final_score


def crossover(parent1, parent2, user_pref):
    # Véletlenszerű keresztezés
    split = random.randint(1, min(len(parent1), len(parent2)) - 1)

    # A szülők filmlistáját kombináljuk
    child = parent1[:split] + parent2[split:]
    
    return child


def mutate(individual, user_pref):
    mutation_point = random.randint(0, len(individual) - 1)

    # A mutáció során egy véletlen filmet választunk, amely illeszkedik a műfaj preferenciákhoz
    valid_movies = filter_movies_by_user_pref(user_pref)

    if valid_movies:  # Ha van érvényes film
        individual[mutation_point] = random.choice(valid_movies)

    return individual


def genetic_algorithm(population_size, generations, user_pref):
    population = [population_inicialization(user_pref) for _ in range(population_size)]
 
   
    for generation in range(generations):
        population.sort(key=lambda x: fitness(x, user_pref), reverse=True)

        parents = population[:2]
        new_population = []


        # Keresztezes es mutacio minden uj egyedhez
        for _ in range(population_size // 2):
            #keresztezes
            child = crossover(parents[0], parents[1], user_pref)
            #mutacio
            child = mutate(child, user_pref)
            #uj egyed hozzaadasa
            new_population.append(child)

        population = new_population
    return remove_duplicates(population[0][:3])



@app.route('/', methods=['GET', 'POST'])
def index():
    genres = get_genres()  
    selected_genres = []  
    user_pref = []  
    best_movies = [] 
    error_message = None

    if request.method == 'POST':
        selected_ids = request.form.getlist('genre')  # mufajok id-jait 
        genre_dict = {str(genre['id']): genre['name'] for genre in genres}
        selected_genres = [genre_dict[genre_id] for genre_id in selected_ids if genre_id in genre_dict]

        user_pref = [int(genre_id) for genre_id in selected_ids]  
        if not user_pref:
            error_message = "Please select at least one genre."
            return render_template('index.html', genres=genres, error_message=error_message)

        movies = get_popular_movies()
        best_movies = genetic_algorithm(population_size=10, generations=20, user_pref=user_pref)
        print(f"Best movies: {best_movies}")

    
    return render_template('index.html', genres=genres, selected_genres=selected_genres, best_movies=best_movies)

if __name__ == '__main__':
    app.run(debug=True)
