import json
import sys

class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            try:
                args = sys.argv[1:]
                with open(args[0] + '_config.json') as f:
                    config = json.load(f)
                    
                    # MSSQL
                    cls._instance.MSSQL_SERVER = config['mssql']['server']
                    cls._instance.MSSQL_DB = config['mssql']['db']
                    cls._instance.MSSQL_USER = config['mssql']['user']
                    cls._instance.MSSQL_PASS = config['mssql']['pass']

                    # Subiekt
                    cls._instance.SUBIEKT_WAREHOUSE = config['subiekt']['warehouse']
                    cls._instance.SUBIEKT_PRICE = config['subiekt']['price']

                    # Sylius
                    cls._instance.SYLIUS_URL = config['sylius']['url']
                    cls._instance.SYLIUS_USER = config['sylius']['user']
                    cls._instance.SYLIUS_PASS = config['sylius']['pass']
                    
            except FileNotFoundError:
                print("Error: Configuration file not found.")
                sys.exit(1)

        return cls._instance