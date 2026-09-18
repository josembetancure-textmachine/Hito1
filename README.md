# Hito 1 — Normalizador de Municipios y Contactos

> English summary: A data-cleaning pipeline that normalizes a 135-record dataset (accents, casing, date formats, contact info) and assigns a priority level to each observation based on its content. Built as the first step of a self-directed transition from philology into data analysis and NLP. (The rest of this document is in Spanish.)

Pipeline de análisis de datos para la limpieza y normalización (acentos, mayúsculas, formato de fecha, contactos) de un dataset de 135 registros que incluye regiones, contactos, nivel de prioridad, fechas y nombres.

## Relevancia

Las observaciones de este dataset describen situaciones de campo que pueden implicar afectaciones a la vida, la salud o los derechos de población vulnerable. Por eso el pipeline no se limita a limpiar y normalizar los datos: también asigna un nivel de prioridad (rojo, naranja, amarillo, verde) según el contenido de cada observación, de manera que los casos más urgentes puedan identificarse de inmediato en vez de perderse entre 135 filas sin clasificar.

## Contexto

Este proyecto se realiza como introducción a la programación orientada al análisis de datos y hace parte de un plan de transición al sector tecnológico que desemboca en el procesamiento del lenguaje natural y, por tanto, incluye SQL, pandas, PyTorch, etc.


## Instalación

Requisitos previos: Python 3.12 o superior. Es un requisito estricto, pues el código usa f-strings con comillas dobles anidadas dentro de otras comillas dobles (una mejora de sintaxis introducida en Python 3.12, PEP 701). En versiones anteriores de Python, esto produce un SyntaxError.

Para la instalación, ejecute lo siguiente:

```bash
git clone https://github.com/josembetancure-textmachine/Hito1.git
cd Hito1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Estos comandos están pensados para Linux/macOS. En Windows, el paso de activación del entorno virtual cambia a .venv\Scripts\activate.

## Uso

Para ejecutar el pipeline correctamente, debe ejecutarse desde Hito1/

```bash
cd Hito1
python3 main.py
```
Es indispensable que el archivo datos_sucios_hito1.csv se encuentre ubicado en la ruta correspondiente: Hito1/data/raw/, pues de lo contrario se producirá un error con el siguiente mensaje: "Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/"

Este pipeline genera un archivo llamado datos_limpios_hito1.csv en Hito1/data/processed/. A diferencia del insumo original, este nuevo archivo contiene los datos de contacto separados en dos nuevas columnas (teléfono y correo), las regiones reasignadas para cada municipio según el input del usuario, los acentos de esas regiones normalizados, mayúsculas normalizadas, fechas en formato día/mes/año para todos los casos y una nueva columna (estado) donde se asigna un nivel de prioridad según la columna de observaciones.

En relación con lo anterior, se debe tener en cuenta que, en caso de que se incluya una nueva fila con un municipio que no hace parte del conjunto original o de que se elimine el JSON de Hito1/interim, el pipeline pedirá que el usuario ingrese manualmente las regiones correspondientes para poder continuar su ejecución.

Debe considerarse que la ruta processed/ se encuentra incluida en .gitignore, por lo que el archivo generado por el pipeline no se encuentra _trackeado_ por el repositorio, sino que se crea al ejecutar el código.

## Estructura del proyecto

```
Hito1/
├── data/
│   ├── raw/          [Contiene el archivo .csv que funciona como insumo, pues contiene los datos originales.]
│   ├── interim/       [Contiene el JSON que funciona para guardar el progreso del usuario cuando ingresa cada región a su municipio correspondiente.]
│   └── processed/     [Contiene el resultado del pipeline. Está en .gitignore porque no se necesita para ejecutar el pipeline.]
├── notebooks/          [Contiene los notebooks .ipynb en los que se exploró el código antes del pipeline final.]
├── main.py             [Es el pipeline consolidado y ejecutable]
├── NOTAS.md            [Archivo de estudio en el que se consignó el proceso de pensamiento al construir el código. Sirve para los reclutadores.]
├── requirements.txt
└── .gitignore
```

## Cambios frente al planteamiento original

- Estados: de 3 categorías a 4. El original agrupaba "prioritario" e "importante" bajo un mismo estado (naranja). La implementación final los separó en dos estados distintos: prioritario → Naranja, importante → Amarillo.
- El original sugiere que verde es el estado por defecto (todo lo que no sea rojo o naranja). En la implementación final, verde solo se asigna cuando el texto contiene indicadores positivos explícitos ("éxito", "sin novedad", "normal").
- El manejo de nombres faltantes o inválidos no estaba contemplado en el original. El original asume que los nombres solo necesitan la corrección en las mayúsculas/minúsculas. Sin embargo, la columna real contenía valores vacíos, "N/A" y "No registra", que se resolvieron con el valor "Sin dato" antes de aplicar el formato de mayúsculas. Lo mismo sucede para los contactos, pues aquellos faltantes se resuelven con la etiqueta "Sin dato".

## Autoría

Para conocer el proceso de desarrollo completo y la postura sobre el uso de IA en este proyecto, ver [NOTAS_HITO1.md](NOTAS_HITO1.md)