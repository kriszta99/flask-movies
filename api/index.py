from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

API_KEY = 'b0ff54d9f03d74a916ff2ecc5fa2ccd0'
BASE_URL = 'https://api.themoviedb.org/3/'

URL = "https://api.themoviedb.org/3/movie/popular"
URL_tv = "https://api.themoviedb.org/3/tv/popular"
PARAMS = {
    "api_key": API_KEY,
    "language": "en-US",
}

"""
def remove_duplicates(movies):
    # letrehozunk egy ures szotarat s a kulcsok a filmek 'id' lesz
    movie_dict = {}
    for movie in movies:
        movie_id = movie['id']  # minden film id-ja lekerese
        # ha a film id-ja letezik a szotarban akkor az uj film felirodik a regivel s csak 1 film marad benne
        movie_dict[movie_id] = movie  
    
    # a szotar ertekeit atalakitjuk listava
    unique_movies = list(movie_dict.values())
    return unique_movies
"""
def remove_duplicates(movies):
    return list({movie['id']: movie for movie in movies}.values())

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


#lekerem a legnepszerubb sorozatokat a TMDB-bol
def get_popular_tv_shows():
    all_tv_shows = []
    for page in range(1,25): 
        # mivel tudom hogy egy oldalon 20 darab film van igy oldalankent kerem le
        PARAMS['page'] = page
        response = requests.get(URL_tv, params=PARAMS)
        if response.status_code == 200:
            data = response.json()
            popular_tv_shows = data.get("results", [])
            all_tv_shows.extend(popular_tv_shows)
        else:
            print(f"Error fetching page {page}: {response.status_code}")
    return all_tv_shows




#lekerem a legnepszerubb filmeket TMDB API-ból
def get_popular_movies():
    all_movies = []
    for page in range(1, 25):  # oldalnyi filmet kerek le mivel 1 oldalon 20 darab van
        PARAMS['page'] = page
        response = requests.get(URL, params=PARAMS)
        if response.status_code == 200:
            data = response.json()
            popular_movies = data.get("results", [])
            all_movies.extend(popular_movies)
        else:
            print(f"Error fetching page {page}: {response.status_code}")
    return all_movies



def population_inicialization(movies):
    return random.sample(movies,50) 


def fitness(individual, user_pref):
    # a filmek pontszamainak tarolasa

    score_per_movie = []
    for movie in individual:
        genre_ids = movie.get("genre_ids", [])  # a film mufajainak ID-jait szedjuk ki

        
        match_score = 0
        #a film mufajainak (genre_ids) azonositoit osszehasonlitjuk a felhasznaloi preferenciakkal (user_pref)
        for genre_id in genre_ids:
            if genre_id in user_pref:
                match_score += 1  # egyezésnél növeljük a pontszámot
        
        # minden filmhez hozzaadjuk a pontszamot
        score_per_movie.append(match_score)
    
    return sum(score_per_movie) 

def crossover(parent1, parent2):
    # veletlenszeru keresztezes
    #print(f"Paren1 :{parent1}")
    #azert indul 1 tol hogy legyen legalabb egy elem mindket szulobol az utodban
    split = random.randint(1, len(parent1) - 1)
    
    # utod letrehozasa ket szulo kombinalasaval
    child = parent1[:split] + parent2[split:]
    
    return child


# mutacio
def mutate(individual, movies):
    #0-tol mivel barmelyik elem kivalaszthato
    mutation_point = random.randint(0, len(individual) - 1)
    individual[mutation_point] = random.choice(movies)
    return individual

def genetic_algorithm(population_size, generations, movies, user_pref):
    # az osszes filmszetett tartalmazza
    population = []
    for _ in range(population_size):
        population.append(population_inicialization(movies))
    #print(f"Populations: {population}")
   
    for generation in range(generations):
        #itt  tortenik a kivalasztas
        # csokkeno sorrendbe rendezi hogy elore keruljenek a legjobb egyed (a legmagasabb fitness pontszamuak)
        population.sort(key=lambda x: fitness(x, user_pref), reverse=True)
        # az elso ketot veszi ki
        parents = population[:2]
        new_population = []


        # uj generacio letrehozasa
        for _ in range(population_size // 2):
    
            #keresztezes -> ket szulo kombinalasaval egy uj gyerek jon letre
            child = crossover(parents[0], parents[1])
            #print(parents[0], parents[1])
            #mutacio -> a gyerek egyed elemet modositja egy veletlenszeru mutacioval     
            child = mutate(child, movies)
            #uj egyed hozzaadasa
            new_population.append(child)
            
            
        
        population = new_population

    population.sort(key=lambda x: fitness(x, user_pref), reverse=True)
    #print(population[0])
    # Csak a legjobb egyed marad az utolsó generációból
    return remove_duplicates(population[0])


@app.route('/', methods=['GET', 'POST'])
def index():
    #lekerem a mufajokat a listaba
    genres = get_genres()  
    selected_genres = []  
    user_pref = []  
    best_movies = [] 
    best_tv_shows = []
    error_message = None
    tv_shows = []

    #ha POST keres van 
    if request.method == 'POST':
        selected_ids = request.form.getlist('genre')  # mufajok id-jait lekerjuk a formbol

        genre_dict = {}
        for genre in genres:
            genre_dict[str(genre['id'])] = genre['name']

        selected_genres = []
        for genre_id in selected_ids:
            if genre_id in genre_dict:
                selected_genres.append(genre_dict[genre_id])

        user_pref = [int(genre_id) for genre_id in selected_ids]  

        if not selected_ids:
            error_message = "Please select at least two genre."
            return render_template('index.html', genres=genres, error_message=error_message)

        movies = get_popular_movies()
        best_movies = genetic_algorithm(population_size=100, generations=50,  movies=movies, user_pref=user_pref)

        tv_shows = get_popular_tv_shows()
        best_tv_shows = genetic_algorithm(population_size=100, generations=50,  movies=tv_shows, user_pref=user_pref)


        print(f"Best tv shows: {best_tv_shows}")
    return render_template('index.html', genres=genres, selected_genres=selected_genres, best_movies=best_movies, best_tv_shows=best_tv_shows)

if __name__ == '__main__':
    app.run(debug=True)
