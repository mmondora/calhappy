import unittest
from calhappy import extract_song_info  # Importa la funzione da calhappy.py


# Classe del test unitario
class TestExtractSongInfo(unittest.TestCase):

    def test_valid_input2(self):
        # Testa un input valido
        quote = "Pianifica le tue ferie con cura e entusiasmo, lasciati ispirare dalla bellezza del mondo e dall'energia delle festività primaverili. Insieme a te, Andrea Tibi e molti altri sognatori. Buona preparazione per il tuo viaggio! 🌸🌍🌙 Soundtrack: Happy by Pharrell Williams"
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "Happy")
        self.assertEqual(artist_name, "Pharrell Williams")

    def test_valid_input(self):
        # Testa un input valido
        quote = "Soundtrack Brave di Sara Bareilles"
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "Brave")
        self.assertEqual(artist_name, "Sara Bareilles")

    def test_missing_keyword(self):
        # Testa un input che non contiene la parola "di"
        quote = "Soundtrack Brave Sara Bareilles"
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "")
        self.assertEqual(artist_name, "")

    def test_empty_input(self):
        # Testa un input vuoto
        quote = ""
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "")
        self.assertEqual(artist_name, "")

    def test_no_song_title(self):
        # Testa una stringa che non contiene "Canzone"
        quote = "Brave di Sara Bareilles"
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "")
        self.assertEqual(artist_name, "")

    def test_incorrect_format(self):
        # Testa una stringa con formato non corretto
        quote = "Musichetta di Sara Bareilles"
        track_title, artist_name = extract_song_info(quote)
        self.assertEqual(track_title, "")
        self.assertEqual(artist_name, "")

if __name__ == "__main__":
    unittest.main()