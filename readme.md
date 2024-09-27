### Uruchomienie skryptu przez PS
```
py -B main.py default
```

### Uruchomienie skryptu na macos
```
python -B main.py default
```

### Przykładowy config
Zapisz plik jako default_config.json
```
{
    "mssql": {
        "server": "192.168.1.100\\SQL",
        "db": "Default",
        "user": "sa",
        "pass": "example"
    },
    "subiekt": {
        "price": "CenaBrutto4",
        "warehouse": "1"
    },
    "sylius": {
        "url": "https://127.0.0.1:8000",
        "user": "api.integracja@example.com",
        "pass": "example"
    },
    "app": {
        "log": true,
        "log_path": "C:\TMP\log\default\"
    }
}
```