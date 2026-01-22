import openai
import json
import datetime
import os
import requests
from typing import List
from datetime import datetime, timedelta, date
import requests
import base64
import os
import argparse
from ics import Calendar, Event  # Importa la libreria per lavorare con i file .ics

# Inserisci il tuo client_id e client_secret ottenuti da Spotify
client_id = os.getenv( "MUSIC_CLIENT_ID" )
client_secret = os.getenv( "MUSIC_CLIENT_SEC")

# Impostazione della chiave API di OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
DEBUG=False

# Funzione per caricare la configurazione dal file JSON
def load_config() -> dict:
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

# Funzione per caricare la storia delle citazioni
def load_quote_history() -> dict:
    if os.path.exists('quote_history.json'):
        with open('quote_history.json', 'r') as f:
            return json.load(f)
    return {}

# Funzione per salvare la storia delle citazioni
def save_quote_history(history: dict) -> None:
    with open('quote_history.json', 'w') as f:
        json.dump(history, f, indent=4)

# Funzione per leggere il prompt da un file esterno
def load_prompt_from_file() -> str:
    with open('prompt.txt', 'r') as file:
        return file.read()

# Funzione per generare una frase ispirazionale con l'autore e il titolo della canzone
def generate_inspirational_quote(subject: str, date: str, time: str, participants: List[str], event_location: str) -> str:
    # Carica la storia delle citazioni
    history = load_quote_history()

    # Leggi il prompt dal file esterno
    prompt = load_prompt_from_file()

    # Sostituisci i segnaposto nel prompt con le informazioni specifiche
    prompt = prompt.format(
        subject=subject,
        date=date,
        time=time,
        event_location=event_location,
        participants=', '.join(participants)
    )

    # Carica la configurazione
    config = load_config()
    model = config["model"]  # Prende il modello dal file di configurazione

    # Ottieni la risposta da OpenAI (usando l'endpoint chat)
    response = openai.chat.completions.create(
        model=model,  # Usa il modello da configurazione
        messages=[{"role": "user", "content": prompt}],  # Formato chat
        max_tokens=150
    )

    # Estrai la risposta dal modello
    quote = response.choices[0].message.content.strip()
    if DEBUG:
        print( f"\nDEBUG generate_inspirational_quote: {quote}" )
    # Estrai anche il titolo e l'autore della canzone dalla risposta (aggiungiamo una parte del testo)
    #song_info = extract_song_info(quote)

    # Salva la frase nella storia
    if date not in history:
        history[date] = []
    history[date].append(quote)
    save_quote_history(history)

    return quote

def generate_soundtrack(inspirational_quote: str) -> str:
    # Definiamo un secondo prompt per generare il titolo del brano basato sulla frase ispirazionale
    prompt = f"Given the following inspirational quote, suggest a music track: {inspirational_quote} in the format 'Song by Artist'. No other information needed"

    # Carica la configurazione
    config = load_config()
    model = config["model"]  # Prende il modello dal file di configurazione

    # Ottieni la risposta da OpenAI (usando l'endpoint chat)
    response = openai.chat.completions.create(
        model=model,  # Usa il modello da configurazione
        messages=[{"role": "user", "content": prompt}],  # Formato chat
        max_tokens=100
    )

    # Estrai il brano musicale e l'artista dalla risposta
    music_info = response.choices[0].message.content.strip()
    if DEBUG:
        print( f"\nDEBUG generate_soundtrack: music info {music_info}")
    song_info = extract_song_info( music_info )
    if DEBUG : 
        print( f"\nDEBUG generate_soundtrack: song info {song_info}" )

    return song_info

# Funzione per estrarre il nome dell'autore e il titolo della canzone dalla frase ispirazionale
def extract_song_info(quote: str) -> tuple:
    # Supponiamo che la frase ispirazionale abbia il formato "Soundtrack [titolo] di [autore]"
    if  "by" in quote:
        # Prima cerchiamo "Soundtrack", poi splittiamo con "di"
        parts = quote.split(" by ")
        if len(parts) == 2:
            track_title = parts[0].strip()  # Rimuovi "Soundtrack" se presente
            artist_name = parts[1].strip()
            return track_title, artist_name
    return "", ""  # Se non viene trovato il formato corretto, restituiamo due stringhe vuote

# Funzione per generare automaticamente il messaggio se non fornito
def generate_email_message(subject: str, person: str) -> str:
    prompt = f"Agisci come un segretario, senza firmarti, e genera un breve invito per ricordare il subject: '{subject}' e per queste persone {person}. Max 200 parole."

    # Carica la configurazione
    config = load_config()
    model = config["model"]  # Prende il modello dal file di configurazione

    response = openai.chat.completions.create(
        model=model,  # Usa il modello da configurazione
        messages=[{"role": "user", "content": prompt}],  # Formato chat
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Funzione per calcolare l'orario di fine (50 minuti dopo l'inizio)
def calculate_end_time(start_time: str) -> str:
    start_time_obj = datetime.strptime(start_time, "%H:%M")
    end_time_obj = start_time_obj + timedelta(minutes=50)  # Aggiungi 50 minuti
    return end_time_obj.strftime("%H:%M")


# Funzione per configurare gli argomenti da linea di comando
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate calendar events with AI-generated inspirational quotes and soundtracks.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 calhappy.py  # Interactive mode
  python3 calhappy.py -s "Team Meeting" -a "john@example.com;jane@example.com" -l "Conference Room"
  python3 calhappy.py --subject "Project Review" --attendees "team@company.com" --location "Online" --date 2026-01-25 --time 14:00
        '''
    )
    parser.add_argument('-s', '--subject', type=str, help='Event subject/title')
    parser.add_argument('-a', '--attendees', type=str, help='Attendees list (separated by ;)')
    parser.add_argument('-l', '--location', type=str, help='Event location')
    parser.add_argument('-d', '--date', type=str, help=f'Event date (YYYY-MM-DD) [default: {date.today()}]')
    parser.add_argument('-t', '--time', type=str, help='Event start time (HH:MM) [default: 09:00]')
    parser.add_argument('-m', '--message', type=str, help='Event message (auto-generated if not provided)')
    return parser.parse_args()

# Funzione principale
def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Ricevi input dall'utente o usa gli argomenti da linea di comando
    if args.subject:
        subject = args.subject
    else:
        subject = input("Inserisci il subject dell'evento: ")

    if args.attendees:
        attendees_input = args.attendees
    else:
        attendees_input = input("Inserisci l'elenco degli invitati (separati da ;): ")

    if args.location:
        event_location = args.location
    else:
        event_location = input("Inserisci il luogo dell'evento: ")

    # Gestione della data
    if args.date:
        date_input = args.date
    else:
        date_input = input(f"Inserisci la data dell'evento (YYYY-MM-DD) [default: {date.today()}]: ")
        if not date_input:
            date_input = str(date.today())

    # Gestione dell'orario di inizio
    if args.time:
        time_input = args.time
    else:
        time_input = input("Inserisci l'ora di inizio dell'evento (HH:MM) [default: 09:00]: ")
        if not time_input:
            time_input = "09:00"  # Orario di default a 09:00

    # Calcolare l'orario di fine (50 minuti dopo l'inizio)
    end_time = calculate_end_time(time_input)

    if args.message is not None:
        message = args.message
    else:
        message = input("Inserisci il messaggio dell'evento (Premi invio per generarlo automaticamente): ")

    # Se il messaggio è vuoto, genera il messaggio basato sul subject
    if not message:
        message = generate_email_message(subject, attendees_input )
        if DEBUG:
            print("\nDEBUG Messaggio generato automaticamente:\n", message)

    attendees = attendees_input.split(';')

    # Genera la frase ispirazionale
    quote = generate_inspirational_quote(subject, date_input, time_input, attendees, event_location)
    song_info = generate_soundtrack( quote )

    # Se il nome della traccia e dell'artista sono stati trovati
    if song_info:
        turl = search_spotify_track(song_info[0], song_info[1])
        track_url = f" {song_info[0]} by {song_info[1]} " + turl 
    else:
        track_url = "Nessuna traccia trovata"

    # Stampa il testo dell'evento con la frase ispirazionale
    print("\n=== Dettagli dell'Evento ===")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    print(f"Luogo: {event_location}")
    print(f"Data: {date_input} dalle {time_input} alle {end_time}")
    print(f"Frase Ispirazionale: {quote}")
    print(f"Soundtrack {track_url}")
    

    file = generate_ics_event(subject, date_input, time_input, end_time, event_location, message + "\n\n" + quote, track_url)
    print(f"\nfile {file}")
    print("\nEvent successfully generated!")

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

# Funzione per generare il file .ics
def generate_ics_event(subject: str, date: str, time: str, end_time: str, location: str, quote: str, music: str):
     # Definisci il percorso della cartella dove vuoi salvare i file .ics
    calendar_folder = "calendar_events"  # Puoi cambiare questo percorso in base alle tue necessità

    # Crea la cartella se non esiste
    if not os.path.exists(calendar_folder):
        os.makedirs(calendar_folder)

    calendar = Calendar()
    event = Event()

    # Impostare il titolo, la data e l'ora dell'evento
    event.name = subject
    event.begin = f"{date} {time}"
    event.end = f"{date} {end_time}"
    event.location = location

    # Aggiungere la descrizione (quote + music)
    event.description = f"{quote}\n\nSoundtrack: {music}"

    # Aggiungere l'evento al calendario
    calendar.events.add(event)

    # Salva il calendario in un file .ics
    file = f"{subject}_{date}.ics"
    ics_file_path = os.path.join(calendar_folder, f"{subject}_{date}.ics")

    with open(ics_file_path, "w") as my_file:
        my_file.writelines(calendar)

    if DEBUG:
        print(f"File {ics_file_path} generato per l'evento '{subject}'")
    return file

# Funzione per cercare una traccia su Spotify
def search_spotify_track(track_name: str, artist_name: str):
    access_token = get_spotify_access_token()  # Ottieni l'access token
    
    search_url = f"https://api.spotify.com/v1/search?q=track:{track_name}+artist:{artist_name}&type=track&limit=1"
    headers = {
        "Authorization": f"Bearer {access_token}"  # Aggiungi il token all'intestazione della richiesta
    }

    if DEBUG: 
        print( f"\nsearch_spotify_track: {track_name} by {artist_name}")
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



if __name__ == "__main__":
    main()