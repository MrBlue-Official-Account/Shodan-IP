# Shodan-IP 

A diferencia de otras de herraminetas **SHODAN IP** no usa una **API**, permite realizar consultas avanzadas a Shodan para extraer direcciones IP y puertos asociados, filtrando resultados por parámetros específicos.

![sshodan_ip](https://github.com/user-attachments/assets/360f38e6-dd83-455c-87c8-e5677c11b1b0)

> [!NOTE]❗Nota:
> regule la cantidad de puertos a filtrar ya que dependerá el tiempo de espera para las IP.  Por defecto son 60 segundos, puede cambiarlo en `timeout=<Time>`

## Características

El script recibe varios argumentos para personalizar la consulta:
- `--query_base`: **Define la consulta(query) base para Shodan.**

- `--facet`: **Filtra los resultados usando "facets" específicos (e.g., port, ip, etc.).**

- `--port`: **Especifica los puertos a buscar, separados por comas.**

- `-o`, `--output`: **Archivo donde guardar los resultados (IP:PORT).**

- `-fh`,`--facet_help`: **Muestra las opciones válidas para usar "facets" desde un archivo YAML.**

## Flujo de Ejecución

A. **Validación Inicial**

- Si usa `-fh`, `--facet_help`, lee el archivo `facets.yaml`, muestra las opciones en formato tabular y terminal.
```sh
python3 shodanip.py -fh
```     

- ![facet](https://github.com/user-attachments/assets/9914d695-c892-4fa8-8936-f11460a6e8b0)

B. **Validación de Puertos**

- Si se proporciona `--port`, verifica que sea una entrada válida (números separados por comas)

C. **Realización de Consultas**

- El script construye consultas para Shodan con base en los argumentos dados.

- Para cada consulta, envía una solicitud `GET` a la URL de Shodan, analizando la respuesta **HTML** para extraer:
    1. IP y puerto(s)
    2. Resultados relacionados (cuando no se usa el argumento `--port`).

D. **Manejo de Resultados**

- Si no se especifica un archivo de salida (`-o`, `--output`), muestra los resultados en formato JSON en la consola. De lo contrario se guardarán en un archivo de texto plano.

## Uso


```sh
git clone https://github.com/4D7220426C7565/Shodan-IP.git; cd Shodan-IP && pip install -r requirements.txt
```

1. **Consulta básica sin puertos:**

```sh
python3 shodanip.py --query_base "\"Set-Cookie: mongo-express=\" \"200 OK\"" --facet port
```
![shodanip](https://github.com/user-attachments/assets/0901c01f-da1e-4bc4-81f2-056653e37fc3)


2. **Consulta específica por puertos:**

```sh
python3 shodanip.py --query_base "\"Set-Cookie: mongo-express=\" \"200 OK\"" --facet ip --port <port>
```
![port](https://github.com/user-attachments/assets/1cbb2508-885e-4d1f-b467-04aa90100912)


3. **Exportar resultados a un archivo:**

```sh
python3 shodanip.py --query_base "\"Set-Cookie: mongo-express=\" \"200 OK\"" --facet ip --port <port> -o <file>
```
![o](https://github.com/user-attachments/assets/a635113b-a5c7-44df-b9e4-bbe473d17040)
