import os
import sys
import logging
import time
from datetime import datetime
from collections import Counter
from rich import print
from rich.console import Console
from rich.table import Table
from alive_progress import alive_bar

from app.config import AppConfig
from app.logger import AppLogger
from app.helper import Helper
from data.subiekt import Subiekt
from data.sylius import Sylius

# Set vars
config = AppConfig()
logger = AppLogger()

# Sylius
logger.text(f"Pobieranie danych [bold blue]Sylius[/bold blue]")
sylius = Sylius()
sylius_variants = sylius.get_variants()
sylius_variants_length = len(sylius_variants)
logger.status("OK", f"({sylius_variants_length} produktów)")
time.sleep(1)

# Subiekt
logger.text(f"Pobieranie danych [bold blue]Subiekt[/bold blue]")
subiekt = Subiekt()
subiekt_products = subiekt.get_products()
subiekt_products_length = len(subiekt_products)
logger.status("OK", f"({subiekt_products_length} produktów)")
time.sleep(1)

# Combine
logger.text(f"Łączenie danych do integracji")
variants = Helper.combine_data(subiekt_products, sylius_variants, config.APP_FULL_INTEGRATION)
variants_length = len(variants)
logger.status("OK", f"({variants_length} produktów)")
time.sleep(1)

# Integrate
try:
    if(variants_length > 0):
        table = Table(show_header=True, header_style="bold", show_lines=True)

        table.add_column("nr", style="dim")
        table.add_column("Wariant", no_wrap=True)
        table.add_column("Aktualizacja", no_wrap=True, width=40)
        table.add_column("Dane Subiekt", no_wrap=True, width=40)
        table.add_column("Dane Sylius", no_wrap=True, width=40)
        table.add_column("Status", width=16)

        logger.text(f"Start integracji")
        time.sleep(1)

        with alive_bar(variants_length) as bar:
            for index, variant in enumerate(variants):

                log_update = "[bold]Stok:[/bold] " + str(variant['stock']) + "\n" \
                    + "[bold]Kod:[/bold] " + variant['code'] + "\n" \
                    + "[bold]Typ:[/bold] " + variant['type'] + "\n" \
                    + "[bold]Ceny:[/bold]"

                for index, (key, item) in enumerate(variant['sylius_variant']['channelPricings'].items()):
                    log_update += "\n" + key + ":"
                    if not bool(item['appliedPromotions']):
                        log_update += "\n - " + "Cena: {:.2f}".format(variant['subiekt_product']['cena'])
                    log_update += "\n - " + "Cena oryginalna: {:.2f}".format(variant['subiekt_product']['cena'])

                log_subiekt = "[bold]ID:[/bold] " + str(variant['subiekt_product']['id']) + "\n" \
                    + "[bold]Symbol:[/bold] " + str(variant['subiekt_product']['symbol']) + "\n" \
                    + "[bold]Dostępne:[/bold] " + str(variant['subiekt_product']['dostepne']) + "\n" \
                    + "[bold]Stok:[/bold] " + str(variant['subiekt_product']['stok']) + "\n" \
                    + "[bold]Rezerwacja:[/bold] " + str(variant['subiekt_product']['rezerwacja']) + "\n" \
                    + "[bold]Cena:[/bold] " + str(variant['subiekt_product']['cena']) + "\n"

                log_sylius = "[bold]ID:[/bold] " + str(variant['sylius_variant']['id']) + "\n" \
                    + "[bold]code:[/bold] " + str(variant['sylius_variant']['code']) + "\n" \
                    + "[bold]onHand:[/bold] " + str(variant['sylius_variant']['onHand']) + "\n" \
                    + "[bold]onHold:[/bold] " + str(variant['sylius_variant']['onHold']) + "\n" \
                    + "[bold]subiektId:[/bold] " + str(variant['sylius_variant']['subiektId']) + "\n" \
                    + "[bold]subiektCode:[/bold] " + str(variant['sylius_variant']['subiektCode']) + "\n" \
                    + "[bold]subiektType:[/bold] " + str(variant['sylius_variant']['subiektType']) + "\n" \
                    + "[bold]channelPricings:[/bold] "

                for index, (key, item) in enumerate(variant['sylius_variant']['channelPricings'].items()):
                    log_sylius += "\n" + key + ":"
                    log_sylius += "\n - " + "price: {:.2f}".format(item['price'] / 100)
                    log_sylius += "\n - " + "originalPrice: {:.2f}".format(item['originalPrice'] / 100)
                    log_sylius += "\n - " + "appliedPromotions: " + (", ".join(p['code'] for p in item['appliedPromotions']) if item['appliedPromotions'] else "null")

                row = [
                    str(index + 1),
                    variant['sylius_variant']['code'],
                    log_update,
                    log_subiekt,
                    log_sylius
                ]

                response = sylius.update_variants(variant)

                if response is not False:
                    if round(variant['subiekt_product']['cena']) > 0:
                        row.append('[green]OK[/green]')
                    else:
                        row.append('[yellow]CENA ZERO[/yellow]')
                else:
                    row.append('[red]BŁĄD[/red]')
                
                table.add_row(*row)

                bar()
        
        # Wyświetlenie tabeli
        logger.table(table)

        logger.text(f"[bold green]Integracja przebiegła prawidłowo![/bold green]")

    else:
        logger.text(f"[bold yellow]Brak produktów do aktualizacji[/bold yellow]")

except Exception as e:
    logger.exception(f"[bold red]Podczas integracji wystąpił błąd![/bold red]", e)

finally:
    logger.save_log()