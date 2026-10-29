import pandas as pd
import json
import numpy as np
import os
import re
from pathlib import Path

#Constantes/configuración

date_formats = ["%d/%m/%y", "%d-%m-%y", "%Y-%m-%d", "%Y/%m/%d", "%b %d, %Y", "%d/%m/%Y"]
months_spa_to_eng = {r"\bEne\b": "Jan", r"\bAbr\b": "Apr", r"\bAgo\b": "Aug", r"\bDic\b": "Dec"}
email_pattern = r"[^\s:]+@[^\s:]+\.[^\s:]+"
phone_pattern = r"\b\d{7,10}\b"

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

def city_territories(city_list, accent_dic, progress=None):
    '''
    Genera un diccionario con cada llave->municipio y su valor->región asignado.

    Args:

        city_list (list): contiene cada municipio que se encuentra en el DataFrame original.
        accent_dic (dict): contiene la región sin tilde, en minúscula y sin espacios; el valor es la región tal como debe escribirse.
        progress (dict, optional): diccionario que contiene cada llave->municipio y su valor->región asignado. Defaults to None.

    Returns:
        dict: diccionario con cada llave->municipio y su respectivo valor->región asignado.
    
    Notes:
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
        territories_processed=accent_dic.get(territories_key,territories_raw.title())


        print(f"Municipio: {c}, región: {territories_processed}")
        city_territories_dic[c]=territories_processed

    return city_territories_dic

def extract_contact(text):
    '''
    Separa los datos de contacto de un campo de texto.

    Args:
        text (str): valor del campo de texto del DataSet original, concretamente de la columna df["Contacto"].
    
    Returns:
        tuple: contacto de teléfono y correo, en ese orden; uno de los dos valores puede tomar 
        la etiqueta "Sin dato" si no se encuentra. Puede devolver, también, dos valores etiquetados "Sin dato" si el campo de texto es NaN o vacío. 
    
    Notes:
        - La función trabaja concretamente con patrones regex para el teléfono y el correo. No depende de los separadores que haya entre los dos datos.
        - Primero se busca el correo. Después, el correo se quita del argumento (text) para que, en caso de que los contenga, sus dígitos no sean susceptibles
        de ser capturados por el patrón del teléfono.
        - El teléfono se busca en lo que haya quedado del paso anterior.
        - El patrón regex para el correo supone que siempre hay espacio entre el separador del correo y el teléfono. Si no hay espacio antes o después del
        separador, el patrón no encuentra el correo con precisión, sino todo lo que halla hasta el siguiente espacio. 
        P. ej.: juan@d.com/3001234567, (Sin dato, juan@d.com/3001234567)
        - El patrón regex del teléfono no cuenta con que haya espacios internos. Si los hay, el patrón no captura bloques de menos de 7 dígitos.
        P. ej.: 300 123 4567, "Sin dato"; 3001234 567, 3001234
        - Si el campo tiene dos teléfonos o dos correos, solo se encuentra el primero que coincida con el patrón para ambos casos.
    '''
    if pd.isna(text) or text.strip()=="":
        return "Sin dato", "Sin dato"

    email_match=re.search(email_pattern, text)
    without_email=re.sub(email_pattern, "", text)
    phone_match=re.search(phone_pattern, without_email)

    if email_match is None:
        email="Sin dato"
    else:
        email=email_match.group()

    if phone_match is None:
        phone="Sin dato"
    else:
        phone=phone_match.group()

    return phone, email

def normalized_dates(dates):
    '''
    Convierte las fechas de distintos formatos al patrón día/mes/año y pone el año con 4 cifras.

    Args:
        dates (pd.Series): columna completa de las fechas del CSV a procesar.

    Returns:
        pd.Series: fechas en formato dd/mm/aaaa o con la etiqueta "Sin dato" cuando la fecha no se pudo procesar.
    
    Notes:
        - Se usaron seis plantillas definidas en date_formats según los patrones encontrados en el CSV original. Cada plantilla se prueba en orden y cada fila
        conserva la fecha leída con la estructura de la primera plantilla que funciona.
        - %y convierte 00-68 en 2000-2068 y 69-99 en 1969-1999.
        - Todo conjunto de dos cifras en la posición inicial de cualquier valor se interpreta como día.
        - Para que %b funcione, cada abreviatura de los meses en español se traduce a su respectiva abreviatura en inglés.
        - La traducción es case sensitive. Por ejemplo, "dic" no se lee y se etiqueta como "Sin dato".
        - Una fecha imposible se marca como "Sin dato", p. ej.: 31/02/26. También se etiqueta así cualquier formato que no esté en las plantillas.
    '''
    translated_months=dates.replace(months_spa_to_eng, regex=True)
    parsed=pd.Series(pd.NaT, index=dates.index)

    for dates_format in date_formats:
        attempt=pd.to_datetime(translated_months, format=dates_format, errors="coerce")
        parsed=parsed.fillna(attempt)

    parsed=parsed.dt.strftime("%d/%m/%Y")
    parsed=parsed.fillna("Sin dato")

    return parsed

def classify_status(observations):
    r'''
    Asigna un nivel de prioridad a cada observación según las palabras clave que contiene.

    Args:
        observations (pd.Series): columna de observaciones del DataFrame original, concretamente df["Observaciones"].

    Returns:
        pd.Series: estado de cada observación ("Rojo", "Naranja", "Amarillo", "Verde" o "Sin clasificar"), con el mismo índice
        de la Serie recibida.

    Notes:
        - El orden de la lista de condiciones es la jerarquía de severidad: Rojo (afectación a la vida o la salud), Naranja
        (afectación a los derechos), Amarillo (sin afectación, pero no fue una entrevista exitosa) y Verde (entrevista normal o exitosa).
        - np.select se queda con la primera condición que se cumple. Por eso, una observación que activa dos reglas recibe el estado
        de mayor severidad, p. ej.: "Urgente: revisar. Todo normal, sin novedad." queda como "Rojo".
        - Las observaciones que no cumplen ninguna regla, o que están vacías, quedan como "Sin clasificar". print_closing_report las
        cuenta al final del pipeline.
        - np.select devuelve un arreglo de numpy sin índice; se envuelve en pd.Series con el índice de la entrada para que cada estado
        corresponda a su fila.
        - El patrón \bnormal\b evita que "anormal" cuente como "normal", pero tampoco reconoce "normalmente".
        - La clasificación se hace por palabras clave, no por análisis semántico: frases como "no se pudo realizar la visita"
        quedan como "Sin clasificar".
    '''
    condiciones=[observations.str.contains(r"urgente|riesgo|fall[ao]s?\b\s*estructural[e]?s?\b",case=False, na=False), #[e]?s? en vez de agrupar (es)?: tolera errores de tipeo de una letra (ej. "estructurale"), decisión deliberada
                 observations.str.contains(r"prioritario|incomplet[ao]?s?\b|recolec\w*\b.*parcial\w*\b",case=False, na=False), #.* (no \s*) permite palabras intermedias, ej. "recolectado de forma parcial", no solo espacios
                 observations.str.contains(r"important", case=False, na=False), #Se verificó que "important" (sin la "e" final) no genera falsos positivos con "importación"/"importador", a diferencia de "import". No fue el motivo original (fue corrección de un typo), pero es una propiedad útil verificada.
                 observations.str.contains(r"[ée]xito[s]?[oa]?|sin novedad|\bnormal\b", case=False, na=False), #[ée] tolera tilde omitida en "éxito". Uso de \b para "normal", de manera tal que no se cuele "anormal".
                 ]

    etiquetas=["Rojo",
               "Naranja",
               "Amarillo",
               "Verde"]

    return pd.Series(np.select(condiciones, etiquetas, default="Sin clasificar"), index=observations.index)


def print_closing_report(df):
    '''
    Imprime un informe de cierre al terminar el pipeline con los registros que el programa no pudo resolver.

    Args:
        df (pd.DataFrame): DataFrame ya procesado, después de guardarse en data/processed/.

    Returns:
        None: la función no devuelve ningún valor, solo imprime el informe en la terminal.

    Notes:
        - Siempre se imprime el número de filas procesadas. Cada aviso, en cambio, solo aparece si hay al menos un caso; si todo se resolvió,
        el informe tiene una sola línea.
        - Se reportan tres casos en los que el programa no pudo hacer su trabajo: observaciones que no coinciden con ninguna regla de estado
        ("Sin clasificar"), municipios sin región asignada y fechas que no coinciden con ninguna plantilla ("Sin dato").
        - Los "Sin dato" de los contactos y de los nombres no se reportan, pues corresponden a datos que faltan en el CSV original, no a fallos
        del programa.
        - No se muestran los índices de las filas afectadas: los valores ya están etiquetados en el CSV y se pueden filtrar con cualquier
        programa que lo abra. Además, el pipeline no elimina ni reordena filas, por lo que cada fila del CSV procesado coincide con la del original.
        - En el caso de las regiones sí se muestra la lista de municipios, porque es lo que el operador debe capturar en el JSON y su tamaño
        no crece con el dataset.
        - Si hay municipios sin región, el programa avisa, pero no se detiene: el CSV se guarda igual. Así se respeta que el operador termine
        la captura con "-" para completarla en otra ejecución.
    '''
    print(f"[INFO] se procesaron {len(df)} filas.")

    unclassified_count = (df["Estado"]=="Sin clasificar").sum()

    if unclassified_count > 0:
        print(f"[AVISO] Observaciones con la etiqueta 'Sin clasificar': {unclassified_count}.")

    na_regions = df["Región"].isna()
    na_count= na_regions.sum()

    if na_count>0:
        towns_without_region=df.loc[na_regions, "Municipio"]
        towns_without_region=towns_without_region.unique()
        towns_without_region=sorted(towns_without_region)
        print(f"[AVISO] Municipios sin región asignada todavía {towns_without_region}. Número de filas sin región: {na_count}.")

    unclassified_date = (df["Fecha_Registro"]=="Sin dato").sum()

    if unclassified_date > 0:
        print(f"[AVISO] Fechas que fueron etiquetadas 'Sin dato': {unclassified_date}.")



#Bloque if __name__=="__main__"

if __name__=="__main__":

    project_root=Path(__file__).resolve().parent
    actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"
    if not actual_file.exists():
        raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")
    df=pd.read_csv(actual_file)

    df["Municipio"]=df["Municipio"].str.strip() #Se normalizan los espacios en Municipio con .str.strip() porque el CSV original puede traer inconsistencias de espacios que impiden que las llaves coincidan exactamente con las del JSON de regiones. Sin esto, el .map() posterior dejaría varias filas sin región asignada. Además, evita que el mismo municipio aparezca dos veces en city_list.
    city_list=df["Municipio"].unique().tolist()
    df_territories_accent=df[df["Región"].str.contains("á|é|í|ó|ú",case=False, na=False)]
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

    rpoint=city_territories(city_list, accent_normalization_dic, progress=data_saved)
    with open (progress_file,"w") as f:
        json.dump(rpoint,f)

    with open(progress_file,"r") as f:
        mapping_dict=json.load(f)

    df["Región"]=df["Municipio"].map(mapping_dict) #Se cruza el diccionario con la tabla original. El diccionario tiene como llave al municipio y la región es el valor. Para buscar en el archivo original las llaves y reemplazar sus valores (cruce con el diccionario). Se usa map en vez de np.where, pues no hay condiciones lógicas que permitan fácilmente la comparación, sino una referencia 1 a 1; np.where es útil para cuando hay condiciones lógicas.

    results_contacts=df["Contacto"].apply(extract_contact).tolist()

    phone_list=[phone for phone,email in results_contacts]
    email_list=[email for phone,email in results_contacts]

    if "Teléfono" not in df.columns:
        df.insert(loc=4,column="Teléfono",value=phone_list)

    if "Correo" not in df.columns:
        df.insert(loc=5,column="Correo",value=email_list)

    if "Contacto" in df.columns:
        df.drop(columns=["Contacto"],inplace=True)

    df["Estado"]=classify_status(df["Observaciones"])

    first_cols=[col for col in df.columns if col not in ["Observaciones","Estado"]]
    new_order=first_cols+["Observaciones","Estado"]
    df=df[new_order]

    names_nodata=df["Nombre_Informante"].isna()|(df["Nombre_Informante"].str.replace(" ","")=="")|(df["Nombre_Informante"].str.contains("N/A",case=False, na=False))|(df["Nombre_Informante"].str.contains("No registra",case=False, na=False))
    df.loc[names_nodata,"Nombre_Informante"]="Sin dato"

    names_data=df["Nombre_Informante"]!="Sin dato"
    df.loc[names_data,"Nombre_Informante"]=df.loc[names_data,"Nombre_Informante"].str.title()

    df["Fecha_Registro"]=normalized_dates(df["Fecha_Registro"])

    saved_output_directory=project_root/"data"/"processed"
    saved_output_directory.mkdir(parents=True, exist_ok=True)
    saved_file=saved_output_directory/"datos_limpios_hito1.csv"

    df.to_csv(saved_file,index=False,encoding="utf-8")

    print_closing_report(df)