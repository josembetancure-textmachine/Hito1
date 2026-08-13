import pandas as pd
import json
import os
import re
from pathlib import Path

#Constantes/configuración

months_map = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

#Funciones

def accent_normalization(text):
    '''
    Elimina acentos ortográficos del input.

    Args:
        text (str): cadena de texto.

    Returns:
        str: cadena de texto sin acentos ortográficos.
    '''
    return (text.lower().strip()
            .replace("á","a")
            .replace("é","e")
            .replace("í","i")
            .replace("ó","o")
            .replace("ú","u"))

def is_input_valid(text):
    '''
    Devuelve un valor boleano true/false según si el input cumple con las condiciones de una cadena de texto según los parámetros de unicode.

    Args:
        text (str): cadena de texto.

    Returns:
        bool: false si el argumento es vacío, 0 o none. Si no es vacío, 0 o none, devolverá true siempre que esté compuesto únicamente por letras (según la categoría 'Letter' de Unicode), incluso si la cadena de texto tiene espacios internos, gracias al uso de replace().
    
    Raises:
        AttributeError: si se pasa un valor sin método .replace() (ej. un int).
    '''
    if not text:
        return False
    return text.replace(" ","").isalpha() #El AttributeError que se menciona no puede ocurrir en el flujo actual, pues a esta función solo llegarán valores tipo str.

def city_territories(city_list,progress=None):
    '''
    Genera un diccionario con cada llave->municipio y su valor->región asignado.

    Args:

        city_list (list): contiene cada municipio que se encuentra en el DataFrame original.
        progress (dict, optional): diccionario que contiene cada llave->municipio y su valor->región asignado. Defaults to None.

    Returns:
        dict: diccionario con cada llave->municipio y su respectivo valor->región asignado.
    
    Raises:
        NameError: si accent_normalization_dic no está definido desde antes.

    Notes:
        Esta función depende de 'accent_normalization_dic', un diccionario que se genera en una función previa. Si no está definido antes de ejecutar esta función
        generará un NameError.

        Para mantener la modularidad, esta función no genera el diccionario 'progress' por sí misma. El diccionario con el que trabaja este argumento viene de afuera, si existe y, si no, lo asume como None.
    '''

    if progress is None:
        city_territories_dic={}
    else:
        city_territories_dic=progress.copy()
    
    for c in city_list:

        if c in city_territories_dic:
            continue

        while True:
            territories_raw=input(f"Ingrese una región para {c}: \n O ingrese '-' para terminar.").strip()
            
            if territories_raw=="-":
                return city_territories_dic
            
            if is_input_valid(territories_raw):
                break
            print ("La región solo puede contener letras.")

        territories_key=accent_normalization(territories_raw)
        territories_processed=accent_normalization_dic.get(territories_key,territories_raw.title())


        print(f"Municipio: {c}, región: {territories_processed}")
        city_territories_dic[c]=territories_processed

    return city_territories_dic

def split_phone_email(text):
    '''
    Separa los datos teléfono/correo según las condiciones impuestas y genera una lista con los mismos o la lista con el valor "Sin dato"
    si text es vacío o NaN.

    Args:
        text (str): cadena de texto. Representa los valores de la columna "Contacto" del DataFrame original.
    
    Returns:
        list: lista. Generada con el método split que contiene los datos teléfono/correo separados o la lista con el valor
        "Sin dato" si text es vacío o NaN.
    
    Raises:
        AttributeError: si text es un tipo de valor diferente a str.
    '''

    if pd.isna(text) or not text:
        return ["Sin dato"]
    elif text.startswith("Cel:"):
        return text.replace(" ","").replace("Cel:","").split("Correo:")
    elif text.startswith("Correo:"):
        return text.replace(" ","").replace("Correo:","").split("Cel:")
    elif "/" in text:
        return text.replace(" ","").split("/")
    elif "-" in text:
        return text.replace(" ","").split("-")
    else:
        return text.split()

def is_phone_email(row):
    '''
    Evalúa cada valor y determina si se trata de teléfono o de correo según las condiciones impuestas.

    Args:
        row (list): lista. Contiene los valores generados por la función split_phone_email.
    
    Returns:
        tuple: tupla. Asigna una etiqueta "phone" o "email" a cada valor de la tupla en ese orden, según las condiciones impuestas, o "Sin dato"
        para el valor (o ambos) faltante.
    
    Raises:
        AttributeError: si row contiene valores que no sean tipo str.
    
    Notes:
        La función depende de que row contenga uno o dos elementos de tipo str.
    '''
    if len(row)==1:
        if row[0].replace(" ","").isdigit():
            phone=row[0]
            email="Sin dato"
        elif "@" in row[0]:
            phone="Sin dato"
            email=row[0]
        elif row[0].replace("@","").replace("_","").replace(".","").isalnum():
            phone="Sin dato"
            email=row[0]
        else:
            phone="Sin dato"
            email="Sin dato"
    else:
        if row[0].replace(" ","").isdigit():
            phone=row[0]
            email=row[1]
        elif "@" in row[0]:
            phone=row[1]
            email=row[0]
        elif row[0].replace("@","").replace("_","").replace(".","").isalnum():
            phone=row[1]
            email=row[0]
        else:
            phone="Sin dato"
            email="Sin dato"

    return phone, email

def numeric_month(match):
    '''
    Convierte el mes textual a su número correspondiente y reorganiza los elementos de la fecha para que coincida con el formato día/mes/año

    Args:
        match (re.Match): objeto de coincidencia entregado automáticamente por .str.replace(), del cual se extraen los grupos nombrados capturados por el patrón.
    
    Returns:
        str: cadena de texto con la fecha normalizada para que coincida con el formato día/mes/año.
    '''
    text_month=match.group("month")
    return f"{match.group("day")}/{months_map[text_month]}/{match.group("year")}"

def month_year_date(match):
    '''
    Reorganiza los elementos de la fecha para que coincidan con el formato día/mes/año

    Args:
        match (re.Match): objeto de coincidencia entregado automáticamente por .str.replace(), del cual se extraen los grupos nombrados capturados por el patrón.
    
    Returns:
        str: cadena de texto con la fecha normalizada para que coincida con el formato día/mes/año
    
    Notes:
        Para resolver los casos ambiguos entre día/mes (o incluso año cuando solo tiene dos dígitos) en posición inicial, la función asume que el primer elemento siempre es un 
        día, pues el formato común en el contexto de creación y uso de este DataFrame es día/mes/año.
    '''
    if len(match.group("a"))==2: 
        return f"{match.group("a")}/{match.group("b")}/{match.group("c")}"
    else:
        return f"{match.group("c")}/{match.group("b")}/{match.group("a")}"

#Bloque if __name__=="__main__"

if __name__=="__main__":

    project_root=Path(__file__).resolve().parent
    actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"
    if not actual_file.exists():
        raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")
    df=pd.read_csv(actual_file)

    city_list=df["Municipio"].unique().tolist()
    df_territories_accent=df[df["Región"].str.contains("á|é|í|ó|ú",case=False)]
    list_accent=df_territories_accent["Región"].unique().tolist() 

    accent_normalization_dic={accent_normalization(a): a for a in list_accent}

    progress_root=project_root/"data"/"interim"
    progress_root.mkdir(parents=True,exist_ok=True)
    progress_file=progress_root/"progress_territories.json"

    if progress_file.exists():
        with open(progress_file, "r") as f: #Se descartó pd.read_json(..., typ='series') para cargar el mapeo de regiones, porque el archivo es técnicamente un diccionario, no un DataFrame — pandas interpretaría las llaves como columnas y los valores como filas, sin índices reales. Es más correcto y directo usar la librería json estándar.
            raw_data_saved=json.load(f)
    else:
        raw_data_saved={}
    data_saved={k.strip():v for k,v in raw_data_saved.items()}

    rpoint=city_territories(city_list, progress=data_saved)
    with open (progress_file,"w") as f:
        json.dump(rpoint,f)

    df["Municipio"]=df["Municipio"].str.strip() #Se normalizan los espacios en Municipio con .str.strip() porque el CSV original trae inconsistencias de espacios que impiden que las llaves coincidan exactamente con las del JSON de regiones. Sin esto, el .map() posterior dejaría varias filas sin región asignada.

    with open(progress_file,"r") as f:
        mapping_dict=json.load(f)

    df["Región"]=df["Municipio"].map(mapping_dict) #Se cruza el diccionario con la tabla original. El diccionario tiene como llave al municipio y la región es el valor. Para buscar en el archivo original las llaves y reemplazar sus valores (cruce con el diccionario). Se usa map en vez de np.where, pues no hay condiciones lógicas que permitan fácilmente la comparación, sino una referencia 1 a 1; np.where es útil para cuando hay condiciones lógicas.

    phone_email=df["Contacto"].apply(split_phone_email).tolist() #Se convierte a lista porque este resultado se usará con un ciclo for no vectorizable, pues contiene valores no uniformes en longitud, pues row puede contener 1 o 2 elementos según el caso.

    results=[]
    for row in phone_email:
        results.append(is_phone_email(row))

    phone_list=[phone for phone,email in results]
    email_list=[email for phone,email in results]

    if "Teléfono" not in df.columns:
        df.insert(loc=4,column="Teléfono",value=phone_list)

    if "Correo" not in df.columns:
        df.insert(loc=5,column="Correo",value=email_list)

    if "Contacto" in df.columns:
        df.drop(columns=["Contacto"],inplace=True)

    fil_red=df["Observaciones"].str.contains(r"urgente|riesgo|fall[ao]s?\b\s*estructural[e]?s?\b",case=False) #[e]?s? en vez de agrupar (es)?: tolera errores de tipeo de una letra (ej. "estructurale"), decisión deliberada
    fil_orange=df["Observaciones"].str.contains(r"prioritario|incomplet[ao]?s?\b|recolec\w*\b.*parcial\w*\b",case=False) #.* (no \s*) permite palabras intermedias, ej. "recolectado de forma parcial", no solo espacios
    fil_yellow=df["Observaciones"].str.contains("important", case=False) #Se verificó que "important" (sin la "e" final) no genera falsos positivos con "importación"/"importador", a diferencia de "import". No fue el motivo original (fue corrección de un typo), pero es una propiedad útil verificada.
    fil_green=df["Observaciones"].str.contains(r"[ée]xito[s]?[oa]?|sin novedad|normal", case=False) #[ée] tolera tilde omitida en "éxito"

    df["Estado"] = pd.NA

    df.loc[fil_red,"Estado"]="Rojo"
    df.loc[fil_orange,"Estado"]="Naranja"
    df.loc[fil_yellow,"Estado"]="Amarillo"
    df.loc[fil_green,"Estado"]="Verde"

    first_cols=[col for col in df.columns if col not in ["Observaciones","Estado"]]
    new_order=first_cols+["Observaciones","Estado"]
    df=df[new_order]

    names_nodata=df["Nombre_Informante"].isna()|(df["Nombre_Informante"].str.replace(" ","")=="")|(df["Nombre_Informante"].str.contains("N/A",case=False))|(df["Nombre_Informante"].str.contains("No registra",case=False))
    df.loc[names_nodata,"Nombre_Informante"]="Sin dato"

    names_data=df["Nombre_Informante"]!="Sin dato"
    df.loc[names_data,"Nombre_Informante"]=df.loc[names_data,"Nombre_Informante"].str.title()

    df["Fecha_Registro"]=df["Fecha_Registro"].str.replace(r"(?P<month>\w{3})\s*(?P<day>\d{2}),\s*(?P<year>\d{2,4})",numeric_month,regex=True)

    df["Fecha_Registro"]=df["Fecha_Registro"].str.replace(r"(?P<a>\d{2,4})[-/](?P<b>\d{2})[-/](?P<c>\d{2,4})",month_year_date,regex=True)

    saved_output_directory=project_root/"data"/"processed"
    saved_output_directory.mkdir(parents=True, exist_ok=True)
    saved_file=saved_output_directory/"datos_limpios_hito1.csv"

    df.to_csv(saved_file,index=False,encoding="utf-8")