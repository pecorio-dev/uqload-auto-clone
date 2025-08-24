import json
import time
import threading
import requests
import urllib.parse

# === CONFIGURATION ===
API_KEY = "mettez-ici-votre-api-key"
BASE_URL = "https://uqload.net/"
CLONE_URL = BASE_URL          # URL pour la requête POST
RESULT_BASE = BASE_URL        # Pour construire l'URL finale

# === En-têtes HTTP tels que fournis pour l'envoi et la réception ===
HEADERS = {
    "Accept": "",
    "Accept-Encoding": "",
    "Accept-Language": "",
    "Cache-Control": "",
    "Content-Type": "",
    "Cookie": "",
    "Origin": "https://uqload.net",
    "Referer": "https://uqload.net/?op=upload_clone",
    "Sec-CH-UA": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Microsoft Edge\";v=\"134\"",
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
}

session = requests.Session()

# === Vérification des infos de compte (optionnel) ===
account_info_url = f"{BASE_URL}api/account/info?key={API_KEY}"
r = session.get(account_info_url, headers=HEADERS)
print("Infos compte :", r.text)
COOKIES = session.cookies.get_dict()
print("Cookies récupérés :", COOKIES)

# === Fonction de lecture et d'analyse du fichier JSON ===
def lire_donnees_json(file_path):
    """
    Charge le fichier JSON et extrait les films.
    Pour chaque film, extrait le titre, l'image (facultatif) et l'URL Uqload si le service est 'uqload'.
    Retourne une liste de dictionnaires.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier JSON : {e}")
        return []

    films_extraits = []
    for film in data:
        titre = film.get("title", "Titre inconnu")
        image_url = film.get("image_url", "")  # Facultatif
        if "links" in film and isinstance(film["links"], list):
            for link in film["links"]:
                if link.get("service", "").lower() == "uqload":
                    url = link.get("url", "")
                    films_extraits.append({
                        "title": titre,
                        "image_url": image_url,
                        "uqload_url": url
                    })
    return films_extraits

# Chargement et analyse du fichier JSON source
films = lire_donnees_json("film_data_results.json")
print(f"{len(films)} films extraits du fichier JSON.")

# On utilise directement la liste extraite pour traiter les liens Uqload
uqload_links = films
print(f"{len(uqload_links)} liens Uqload extraits.")

# === Variables partagées et synchronisation ===
updated_links = []
processed_links = set()
data_lock = threading.Lock()

# === Fonction de traitement d'un lien ===
def process_link(item):
    attempts = 2
    for attempt in range(attempts):
        try:
            # Transformation du lien si nécessaire (passage de "embed-" à une URL standard)
            url_to_clone = item["uqload_url"]
            if "embed-" in url_to_clone:
                print(f"Transformation du lien embed pour {item['title']}")
                url_to_clone = url_to_clone.replace("embed-", "")
                print(f"  Lien transformé : {url_to_clone}")
            print(f"Processing: {url_to_clone}")
            
            # Préparation des données du POST
            payload = {
                "op": "upload_clone",
                "urls": url_to_clone,
                "submit_btn": "Clone URLs",
                "key": API_KEY
            }
            
            # Envoi de la requête POST sans suivre la redirection
            response = session.post(CLONE_URL, data=payload, headers=HEADERS, cookies=COOKIES, allow_redirects=False)
            if response.status_code != 302:
                raise Exception(f"Statut inattendu : {response.status_code}")
            
            location = response.headers.get("Location")
            if not location:
                raise Exception("En-tête Location manquant dans la réponse")
            
            # Extraction du paramètre 'fn' depuis l'URL de redirection
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(location).query)
            fn_list = parsed.get("fn")
            if not fn_list:
                raise Exception("Paramètre 'fn' introuvable dans l'URL de redirection")
            fn_value = fn_list[0]
            new_uqload_link = f"{RESULT_BASE}{fn_value}.html"
            if not new_uqload_link.endswith(".html"):
                raise Exception(f"Lien invalide récupéré : {new_uqload_link}")
            
            # Vérification par une requête GET sur le nouveau lien
            get_response = session.get(new_uqload_link, headers=HEADERS, cookies=COOKIES)
            if get_response.status_code != 200:
                raise Exception(f"Erreur GET pour {new_uqload_link}: statut {get_response.status_code}")
            
            print(f"✅ {item['title']} -> {new_uqload_link}")
            
            # Sauvegarde des résultats dans le fichier de sortie
            with data_lock:
                if item["uqload_url"] not in processed_links:
                    processed_links.add(item["uqload_url"])
                    updated_links.append({
                        "title": item["title"],
                        "image_url": item["image_url"],
                        "uqload_old_url": item["uqload_url"],
                        "uqload_new_url": new_uqload_link
                    })
                    with open("uqload_updated_links.json", "w", encoding="utf-8") as file:
                        json.dump(updated_links, file, indent=4, ensure_ascii=False)
            break  # Traitement réussi

        except Exception as e:
            print(f"❌ Erreur pour {item['title']} - {e}")
            if attempt < attempts - 1:
                time.sleep(1)
                continue
            else:
                break

# === Séparation des liens en pairs et impairs pour éviter les doublons ===
pair_links = [item for index, item in enumerate(uqload_links) if index % 2 == 0]
impar_links = [item for index, item in enumerate(uqload_links) if index % 2 != 0]

def process_links_thread(links):
    for link in links:
        process_link(link)

# Exécution sur deux threads séparés
thread1 = threading.Thread(target=process_links_thread, args=(pair_links,))
thread2 = threading.Thread(target=process_links_thread, args=(impar_links,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("✅ Processus terminé. Résultats enregistrés dans 'uqload_updated_links.json'.")

