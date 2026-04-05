from services.context_service import test_reverse_search

# Test avec une image célèbre pour vérifier si l'API répond bien
# Exemple : Une photo de la Tour Eiffel ou d'un événement connu
IMAGE_TEST = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Tour_Eiffel_2014.jpg/800px-Tour_Eiffel_2014.jpg"

if __name__ == "__main__":
    test_reverse_search(IMAGE_TEST)