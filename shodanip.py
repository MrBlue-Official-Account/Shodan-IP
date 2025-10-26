"""
    #-------- Extract IP address from shodan By ports
"""
# pylint: disable=C0301,C0410
import json
import re
import sys, os
import argparse
import requests
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
import yaml
from tabulate import tabulate

#NOTE - Initialization of 'colorama' if on Windows
init(autoreset=True)

R = Style.RESET_ALL
Br = Style.BRIGHT
B = Fore.BLUE
Rd = Fore.RED
W = Fore.WHITE

print(Br + B + "############################" + R)
print(Br + B + f"# {R}╔═╗┬ ┬┌─┐┌┬┐┌─┐┌┐┌  ╦╔═╗ {Br}{B}#" + R)
print(Br + B + f"# {R}╚═╗├─┤│ │ ││├─┤│││  ║╠═╝ {Br}{B}#" + R)
print(Br + B + f"# {R}╚═╝┴ ┴└─┘─┴┘┴ ┴┘└┘  ╩╩   {Br}{B}#" + R)
print(Br + B + "############################\n" + R)

parser = argparse.ArgumentParser(description="Consulta en Shodan con argumentos")
parser.add_argument("--query_base", help="Consulta base para Shodan")
parser.add_argument("--facet", help="Facet para filtrar la búsqueda")
parser.add_argument("--port", help="Puerto(s) opcionales, separados por comas (Ej: 80,443)")
parser.add_argument("-o", "--output", help="Archivo de salida para guardar las IPs y puertos en texto plano")
parser.add_argument("-fh", "--facet_help", action="store_true", help="Tabla con las opciones válidas de facet")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

#! Show facet options: '-fh'
if args.facet_help:
    try:
        # Load the facets.yaml file
        with open("./facets.yaml", "r", encoding="utf-8") as file:
            facets = yaml.safe_load(file)["facets"]

        # Convert data into a tabular format
        table = [
            [Br + B + facet, W + description + R] for facet, description in facets.items()
        ]
        # Display the table
        output = tabulate(table, headers=["Facet", "Descripción"], tablefmt="mediawiki")
        output_no_header = re.sub(r'\{\|.*\n', '{|\n', output)
        print(output_no_header)
    except FileNotFoundError:
        print("Error: 'facets.yaml' No se encontró el archivo.")
    except yaml.YAMLError as e:
        print(f"Error al leer el archivo YAML: {e}")
    sys.exit(0)

# Validate port input if provided
if args.port:
    if re.fullmatch(r"(\d+,?)*\d+", args.port):
        ports = args.port.split(",")  # Split ports by commas
        queries = [f"{args.query_base} port:{port}" for port in ports]  # Create queries for each port
    else:
        print(Br + Rd + "Entrada inválida en el puerto. Ingresa solo números separados por comas." + R)
        sys.exit(0)
else:
    queries = [args.query_base]

# Parameters for the GET request
params = {
    "facet": args.facet
}

# Dictionary to store results by port
results_by_port = {}

try:
    for query in queries:
        # Extract the port from the query (if present)
        match = re.search(r"port:(\d+)", query)
        if match:
            port = match.group(1)
        else:
            port = "unknown"

        params["query"] = query

        response = requests.get("https://www.shodan.io/search/facet?", params=params, timeout=60)
        response.raise_for_status()

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the total count in the <span> within <h6 class="grid-heading">
        total_span = soup.find('h6', class_='grid-heading').find('span')
        total = total_span.get_text().strip() if total_span else "Not found"

        # Find all <strong> tags in the HTML (containing IPs)
        results = soup.find_all('strong')
        results_text = [result.get_text().strip() for result in results]

        if not args.port:
            # Find values in <div class="one column value">
            facet_values = soup.find_all('div', class_='one column value')
            facet_values_text = [value.get_text().strip() for value in facet_values]

            # Create a dictionary of associated results
            associated_results = {
                f"{result}": value
                for result, value in zip(results_text, facet_values_text)
            }
            # Store results by query
            results_by_port[f"query: {query} ({total})"] = associated_results
        else:
            # If --port is used, return only the <strong> results
            results_by_port[f"query: {query} ({total})"] = results_text

    # Display the final JSON results if no output file is specified
    if not args.output:
        print(json.dumps(results_by_port, indent=4, ensure_ascii=False))
    else:
        path_file = os.path.abspath(args.output)
        # Save only the IPs and ports in the output file
        with open(args.output, "w", encoding="utf-8") as file:
            for query, results in results_by_port.items():
                if not args.port:
                    unique_ips = set(results)  # Usamos un set para eliminar duplicados
                    file.write(",".join(unique_ips) + "\n")
                else:  # Si se especifica el puerto, escribimos IPs y puertos en líneas separadas
                    match = re.search(r"port:(\d+)", query)
                    port = match.group(1) if match else "unknown"
                    for ip in results:
                        file.write(f"{ip}:{port}\n")

        print(f"{Br}{W}PATH:{R} {path_file}")

except requests.exceptions.RequestException as e:
    print(f"{Br}{W}Ocurrió un error al realizar la solicitud:{R} {e}")
