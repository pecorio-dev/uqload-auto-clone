import json
import requests
import time

# Clé TMDB et URL de recherche
TMDB_KEY = "mettez-votre-api-key-de-tmdb-ici"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"

# Fichier source et fichier SQL de sortie
JSON_FILE = "uqload_updated_links.json"
SQL_FILE = "movies.sql"

# Charger les films depuis le fichier JSON
with open(JSON_FILE, "r", encoding="utf-8") as f:
    movies = json.load(f)

# Ouvrir le fichier SQL en écriture
with open(SQL_FILE, "w", encoding="utf-8") as sql_file:
    # Écriture de la commande de création de table
    sql_file.write("""\
CREATE TABLE IF NOT EXISTS movies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  image_url TEXT,
  uqload_old_url TEXT,
  uqload_new_url TEXT,
  tmdb_id INTEGER,
  tmdb_title TEXT,
  tmdb_overview TEXT,
  tmdb_release_date TEXT,
  tmdb_vote_average REAL
);
\n""")

    def escape_sql(s):
        """Échappe les apostrophes pour l'insertion dans SQL."""
        return s.replace("'", "''") if s else s

    total = len(movies)
    for index, movie in enumerate(movies):
        title = movie.get("title", "")
        image_url = movie.get("image_url", "")
        uqload_old_url = movie.get("uqload_old_url", "")
        uqload_new_url = movie.get("uqload_new_url", "")

        # Valeurs par défaut pour les données TMDB
        tmdb_id = None
        tmdb_title = ""
        tmdb_overview = ""
        tmdb_release_date = ""
        tmdb_vote_average = None

        # Recherche dans l'API TMDB (boucle jusqu'à succès)
        while True:
            try:
                params = {
                    "api_key": TMDB_KEY,
                    "query": title,
                    "language": "fr-FR"
                }
                response = requests.get(TMDB_SEARCH_URL, params=params)
                if response.status_code != 200:
                    print(f"Erreur TMDB pour '{title}': statut {response.status_code}.")
                    input("TMDB bloque ou erreur – connectez votre VPN puis appuyez sur Enter pour réessayer...")
                    continue

                data = response.json()
                results = data.get("results", [])
                if results:
                    result = results[0]  # On prend le premier résultat
                    tmdb_id = result.get("id")
                    tmdb_title = result.get("title", "")
                    tmdb_overview = result.get("overview", "")
                    tmdb_release_date = result.get("release_date", "")
                    tmdb_vote_average = result.get("vote_average")
                break  # Sortir de la boucle en cas de succès

            except Exception as e:
                print(f"Exception lors de la requête TMDB pour '{title}': {e}")
                input("Erreur ou blocage – connectez votre VPN puis appuyez sur Enter pour réessayer...")

        # Préparation de la requête INSERT
        insert_sql = f"INSERT INTO movies (title, image_url, uqload_old_url, uqload_new_url, tmdb_id, tmdb_title, tmdb_overview, tmdb_release_date, tmdb_vote_average) VALUES ('{escape_sql(title)}', '{escape_sql(image_url)}', '{escape_sql(uqload_old_url)}', '{escape_sql(uqload_new_url)}', "
        if tmdb_id is None:
            insert_sql += "NULL, "
        else:
            insert_sql += f"{tmdb_id}, "
        insert_sql += f"'{escape_sql(tmdb_title)}', '{escape_sql(tmdb_overview)}', '{escape_sql(tmdb_release_date)}', "
        if tmdb_vote_average is None:
            insert_sql += "NULL"
        else:
            insert_sql += f"{tmdb_vote_average}"
        insert_sql += ");\n"

        sql_file.write(insert_sql)
        print(f"Traité {index+1}/{total} : {title}")

print(f"\n✅ Fichier SQL généré avec succès : {SQL_FILE}")
