import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from app.config import AppConfig

class HTTP:
    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.config = AppConfig()

    # GET
    def get(self, path, headers = {}):
        try:
            # Wysłanie zapytania GET
            response = requests.get(self.config.SYLIUS_URL + path, headers=headers, verify=False)

            # Sprawdzenie, czy zapytanie zostało wykonane prawidłowo
            if response.status_code == 200:
                return response.json()
            else:
                print('Wystąpił błąd:', response.status_code)
                return False

        except requests.exceptions.RequestException as e:
            print('Wystąpił błąd podczas wysyłania zapytania:', e)
            return False
    
    # POST
    def post(self, path, headers = {}, data = {}):
        try:
            # Wysłanie zapytania POST z danymi w formacie JSON
            response = requests.post(self.config.SYLIUS_URL + path, json=data, headers=headers, verify=False)

            # Sprawdzenie, czy zapytanie zostało wykonane prawidłowo
            if response.status_code == 200:
                return response.json()
            else:
                print('Wystąpił błąd:', response.status_code)
                return False

        except requests.exceptions.RequestException as e:
            print('Wystąpił błąd podczas wysyłania zapytania:', e)
            return False
    
    # PUT
    def put(self, path, headers = {}, data = {}):
        try:
            # Wysłanie zapytania POST z danymi w formacie JSON
            response = requests.put(self.config.SYLIUS_URL + path, json=data, headers=headers, verify=False)

            # Sprawdzenie, czy zapytanie zostało wykonane prawidłowo
            if response.status_code == 200:
                return response.json()
            else:
                print('Wystąpił błąd:', response.status_code)
                return False

        except requests.exceptions.RequestException as e:
            print('Wystąpił błąd podczas wysyłania zapytania:', e)
            return False