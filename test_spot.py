import requests
import base64
import os


# Inserisci il tuo client_id e client_secret ottenuti da Spotify
client_id = os.getenv( "MUSIC_CLIENT_ID" )
client_secret = os.getenv( "MUSIC_CLIENT_SEC")

# Funzione per ottenere l'access token tramite client_credentials
def get_spotify_access_token():
    # Codifica client_id e client_secret in base64
    auth_string = f"{client_id}:{client_secret}"
    auth_string_base64 = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_string_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, headers=headers, data=data)
    
    # Se la richiesta è riuscita, restituisci l'access token
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("access_token")
    else:
        raise Exception(f"Error in obtaining token: {response.status_code}, {response.text}")

# Funzione per cercare una traccia su Spotify
def search_spotify_track(track_name: str, artist_name: str):
    access_token = get_spotify_access_token()  # Ottieni l'access token
    
    search_url = f"https://api.spotify.com/v1/search?q=track:{track_name}+artist:{artist_name}&type=track&limit=1"
    headers = {
        "Authorization": f"Bearer {access_token}"  # Aggiungi il token all'intestazione della richiesta
    }
    
    # Esegui la ricerca sulla API di Spotify
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['tracks']['items']:
            # Se la traccia è trovata, restituisci il link
            track_url = data['tracks']['items'][0]['external_urls']['spotify']
            return track_url
        else:
            return "Traccia non trovata."
    else:
        return f"Errore nella richiesta: {response.status_code}"

# Esempio di utilizzo:
artist = "Sara Bareilles"
track_title = "Brave"
track_url = search_spotify_track(track_title, artist)
print("Link Spotify:", track_url)

# Esempio di utilizzo:
artist = "Sara Bareilles"
track_title = "Brave"
track_url = search_spotify_track(track_title, artist)
print("Link Spotify:", track_url)