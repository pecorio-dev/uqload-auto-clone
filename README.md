# uqload-auto-clone

**uqload-auto-clone** est un projet Python qui automatise le clonage et la mise à jour des liens vidéo hébergés sur Uqload. Ce projet permet de transformer les liens Uqload (même ceux commençant par "embed-") pour obtenir des URLs finales valides se terminant par ".html", d'enrichir ces données avec des informations détaillées sur les films issues de l'API TMDB, puis de générer un script SQL prêt à être importé dans une base de données.

## Fonctionnalités

- **Clonage automatique des liens Uqload**  
  Transforme les liens d’upload clone en URLs finales valides.

- **Gestion des requêtes HTTP optimisée**  
  Utilisation d’en-têtes HTTP et de cookies pour simuler un navigateur réel et éviter les blocages.

- **Intégration avec TMDB**  
  Recherche des informations détaillées sur les films (titre, résumé, date de sortie, note, etc.) via l'API TMDB.  
  En cas de limitation (TMDB bloque les requêtes trop rapides), le script attend que vous appuyiez sur Enter après connexion à un VPN pour reprendre le traitement.

- **Génération de fichier SQL**  
  Crée un script SQL qui contient la commande de création d’une table et des instructions `INSERT` pour alimenter une base de données avec les données combinées Uqload/TMDB.

## Prérequis

- **Python 3.x**
- **Modules Python :**
  - `requests`
- **Accès Internet** (et éventuellement un VPN pour contourner les limitations de l'API TMDB)

## Installation

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/votre-utilisateur/uqload-auto-clone.git
   cd uqload-auto-clone
   ```

2. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```

   _Si le fichier `requirements.txt` n'est pas présent, installez manuellement le module `requests` :_

   ```bash
   pip install requests
   ```

## Utilisation

1. **Génération des liens clonés :**  
   Exécutez le script de clonage qui va récupérer les liens Uqload, les transformer et enregistrer les résultats dans le fichier `uqload_updated_links.json`.

2. **Enrichissement via l'API TMDB et génération du fichier SQL :**  
   Lancez le script qui récupère les informations sur les films via TMDB (en recherchant par titre) et génère un fichier SQL (ex. `movies.sql`).  
   Si l'API TMDB bloque la requête, le script vous invitera à appuyer sur Enter afin de vous connecter à un VPN ou d'attendre avant de reprendre.

   Exemple de commande :
   ```bash
   python3 script_tmdb_to_sql.py
   ```

3. **Importation dans votre base de données :**  
   Utilisez le fichier SQL généré (`movies.sql`) pour créer la table et insérer les données dans votre système de gestion de base de données.

## Configuration

- **Clé TMDB :**  
  La clé API TMDB utilisée est `XXXXXXXXXXXXXXXXXXXXXXX`.  
  Vous pouvez la modifier directement dans le script selon vos besoins.

- **Fichiers sources :**  
  Assurez-vous que le fichier `uqload_updated_links.json` se trouve dans le même répertoire que le script de génération SQL.

## Contribution

Les contributions sont les bienvenues !  
Si vous souhaitez améliorer le projet, n'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence [MIT](LICENSE).

---

**uqload-auto-clone** simplifie la gestion et l'intégration des contenus vidéo en automatisant le processus de clonage et d'enrichissement des liens. N'hésitez pas à signaler des problèmes ou à proposer des améliorations !

