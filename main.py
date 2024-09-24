import os
import sys
import time
from collections import Counter
from rich import print
from rich.console import Console
from rich.table import Table
from alive_progress import alive_bar

from app.helper import Helper
from data.subiekt import Subiekt
from data.sylius import Sylius

# Set vars
console = Console()

# Clear Screen
os.system('cls' if os.name == 'nt' else 'clear')

# Sylius
console.log(f"Pobieranie danych [bold blue]Sylius[/bold blue]")
sys.stdout.write("\033[F")
sys.stdout.write("\033[50G")
sylius = Sylius()
sylius_variants = sylius.get_variants()
sylius_variants_length = len(sylius_variants)
print(f"[bold green]OK[/bold green] [white dim]({sylius_variants_length} produktów)[/white dim]")
time.sleep(1)

# Subiekt
console.log(f"Pobieranie danych [bold blue]Subiekt[/bold blue]")
sys.stdout.write("\033[F")
sys.stdout.write("\033[50G")
subiekt = Subiekt()
subiekt_products = subiekt.get_products()
subiekt_products_length = len(subiekt_products)
console.print(f"[bold green]OK[/bold green] [white dim]({subiekt_products_length} produktów)[/white dim]")
time.sleep(1)

# Combine
console.log(f"Łączenie danych do integracji")
sys.stdout.write("\033[F")
sys.stdout.write("\033[50G")
variants = Helper.combine_data(subiekt_products, sylius_variants)
variants_length = len(variants)
console.print(f"[bold green]OK[/bold green] [white dim]({variants_length} produktów)[/white dim]")
time.sleep(1)

# Integrate
try:
    if(variants_length > 0):
        table = Table(show_header=True, header_style="bold", show_lines=True)

        table.add_column("nr", style="dim")
        table.add_column("Wariant", no_wrap=True)
        table.add_column("Aktualizacja", no_wrap=True, width=36)
        table.add_column("Dane Subiekt", no_wrap=True, width=36)
        table.add_column("Dane Sylius", no_wrap=True, width=36)
        table.add_column("Status", width=12)

        console.log(f"Start integracji")
        time.sleep(1)
        console.print("")

        with alive_bar(variants_length) as bar:
            for index, variant in enumerate(variants):

                log_update = "[bold]Stok:[/bold] " + str(variant['stock']) + "\n" \
                    + "[bold]Kod:[/bold] " + variant['code'] + "\n" \
                    + "[bold]Typ:[/bold] " + variant['type'] + "\n" \
                    + "[bold]Ceny:[/bold]"
                
                for index, item in enumerate(variant['pricing']):
                    log_update += "\n" + item['code'] + " - " + "{:.2f}".format(item['price'] / 100)

                log_subiekt = "[bold]ID:[/bold] " + str(variant['subiekt_product']['id']) + "\n" \
                    + "[bold]Symbol:[/bold] " + str(variant['subiekt_product']['symbol']) + "\n" \
                    + "[bold]Dostępne:[/bold] " + str(variant['subiekt_product']['dostepne']) + "\n" \
                    + "[bold]Stok:[/bold] " + str(variant['subiekt_product']['stok']) + "\n" \
                    + "[bold]Rezerwacja:[/bold] " + str(variant['subiekt_product']['rezerwacja']) + "\n" \
                    + "[bold]Cena:[/bold] " + str(variant['subiekt_product']['cena']) + "\n"

                log_sylius = "[bold]ID:[/bold] " + str(variant['sylius_variant']['id']) + "\n" \
                    + "[bold]Kod:[/bold] " + str(variant['sylius_variant']['code']) + "\n" \
                    + "[bold]onHand:[/bold] " + str(variant['sylius_variant']['onHand']) + "\n" \
                    + "[bold]onHold:[/bold] " + str(variant['sylius_variant']['onHold']) + "\n" \
                    + "[bold]SubiektId:[/bold] " + str(variant['sylius_variant']['subiektId']) + "\n" \
                    + "[bold]SubiektCode:[/bold] " + str(variant['sylius_variant']['subiektCode']) + "\n" \
                    + "[bold]SubiektType:[/bold] " + str(variant['sylius_variant']['subiektType']) + "\n" \
                    + "[bold]Ceny:[/bold] "

                for index, (key, item) in enumerate(variant['sylius_variant']['channelPricings'].items()):

                    log_sylius += "\n" + key + " - " + "{:.2f}".format(item['price'] / 100)

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
        console.print("", table, "")

        console.log(f"[bold green]Integracja przebiegła prawidłowo![/bold green]")

    else:
        console.log(f"[bold yellow]Brak produktów do aktualizacji[/bold yellow]")

except Exception as e:
    console.log(f"[bold red]Podczas integracji wystąpił błąd![/bold red]")
    console.print("\r\n", e)

console.print("")