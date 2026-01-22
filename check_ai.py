from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Impostazione della chiave API

# Funzione per caricare la configurazione dal file JSON
def load_config() -> dict:
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

# Funzione per generare un completamento
def generate_completions(prompt: str) -> str:
    # Carica la configurazione
    config = load_config()
    model = config["model"]  # Prende il modello dal file di configurazione

    # Richiesta al modello utilizzando l'endpoint chat
    response = client.chat.completions.create(model=model,  # Usa il modello da configurazione
    messages=[{"role": "user", "content": prompt}],  # Formato chat
    max_tokens=50)

    return response.choices[0].message.content.strip()

# Esegui un esempio di richiesta
prompt = "Say something creative."
response = generate_completions(prompt)
print(response)