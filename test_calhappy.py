import unittest
from calhappy import generate_inspirational_quote  # Importa la funzione che vuoi testare
import os
from unittest.mock import patch

class TestGenerateInspirationalQuote(unittest.TestCase):

    @patch('openai.resources.chat.Completions.create')
    def test_generate_inspirational_quote(self, mock_openai):
        # Impostiamo un valore mockato per la risposta di OpenAI
        mock_openai.return_value = {
            'choices': [{'message': {'content': 'Frase ispirazionale generata con successo.'}}]
        }

        # Dati di input per il test
        date = "2025-04-04"
        time = "09:00"
        participants = ["andrea@example.com", "maria@example.com"]
        event_location = "Roma"
        subject = "pianificare le ferie"

        # Chiamata alla funzione che vogliamo testare
        result, song_info = generate_inspirational_quote(subject, date, time, participants, event_location)

        # Verifica che la risposta sia corretta
        self.assertEqual(result, 'Frase ispirazionale generata con successo.')

    @patch('openai.resources.chat.Completions.create')
    def test_invalid_date_format(self, mock_openai):
        # Simuliamo una risposta generata da OpenAI
        mock_openai.return_value = {
            'choices': [{'message': {'content': 'Frase ispirazionale generata con successo.'}}]
        }

        # Dati di input con formato data non valido
        date = "205-05-07"  # Formato data sbagliato
        time = "08:00"
        participants = ["andrea@example.com"]
        event_location = "Milano"
        subject = "pianificare le ferie"

        # Chiamata alla funzione (il test si concentra sulla gestione dell'errore del formato data)
        with self.assertRaises(ValueError):
            generate_inspirational_quote(subject, date, time, participants, event_location)

if __name__ == '__main__':
    unittest.main()