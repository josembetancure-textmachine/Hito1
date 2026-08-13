# 01_explore_regions.ipynb

## Primer módulo: generación de los dataframes necesarios.

```python
df_territories_city=pd.read_csv("~/Escritorio/Hito1/data/raw/datos_sucios_hito1.csv")
df_territories_city
```

1. La línea de pandas que uso para abrir el archivo que contiene los datos. El "~" significa, en sistemas basados en unix, como Linux, la carpeta principal del usuario. pd es el acortamiento universal para pandas cuando lo importo como "import pandas as pd". 
    - Debo considerar el uso de pathlib, pues la ruta indicada es relativa a mi máquina.

**Sin embargo:**
1. Usar ~ no es la práctica correcta, pues se genera una ruta relativa a mi máquina que, muy probablemente, no funcionará en otras. Para esto, puedo usar Pathlib, que me sirve para manejar rutas más robustas y, al mismo tiempo, más flexibles. El código definitivo es el siguiente:

```python
current_directory= Path.cwd()
project_root=current_directory.parent
actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"

if not actual_file.exists():
    raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")

df_territories_city=pd.read_csv(actual_file)
df_territories_city
```
2. El raise detiene la ejecución del código con un mensaje explicativo en caso de que no exista el archivo con el insumo. 

Las bondades de Pathlib sobre lo demás, se explicarán más adelante en la creación del archivo con los datos limpios.

## Segundo módulo: extracción de valores únicos por columna "Municipios"
```python
city_list=df_territories_city["Municipio"].unique().tolist() #Opción mpas eficiente para el manejo de recursos.
city_list
```

1. Aquí genero una lista a partir del dataframe original. Con los métodos unique() solo obtengo los valores únicos de la columna "Municipio". Esto es útil para que el programa no me pida un municipio todas las veces que aparezca. Con tolist(), convierto todo en lista de una vez.

**Otras opciones usadas y descartadas:**
```python
    # city_columns=["Municipio"]
    # df_city=pd.read_csv("./datos_sucios_hito1.csv",usecols=city_columns)
    # df_city

    #Opción ganadora por eficiencia de recursos
    # df_city=df_territories_city[["Municipio"]]
    # df_city
 ```
Esta última opción la descarté, sin embargo, porque agrega un paso innecesario a esto, pues desde el principio puedo crear la lista directamente.

## Tercer módulo: normalización de acentos

```python
df_territories_accent=df_territories_city[df_territories_city["Región"].str.contains("á|é|í|ó|ú",case=False)]
list_accent=df_territories_accent["Región"].unique().tolist()
list_accent
```

1. Los usuarios son expertos en no usar tildes, pero el manejo de datos precisos las requiere. Una tilde puede distinguir dos conceptos distintos entre sí. Por eso genero un dataframe, a partir del original, que contenga únicamente las regiones (que finalmente serán el input del usuario) que tienen tilde. Es importante notar la sintaxis: esto es una máscara booleana. A simple vista, parece redundante, pero tiene un sentido lo que está dentro de corchetes es el filtro que se aplica a lo que esta fuera. Es muy explícito. Uno podría aplicar un filtro con los datos de una Tabla A a una Tabla B. Es raro, pero posible.

## Cuarto módulo: funciones para validar el input.
### Normalización de acentos
```python
def accent_normalization(text):
    return (text.lower().strip()
            .replace("á","a")
            .replace("é","e")
            .replace("í","i")
            .replace("ó","o")
            .replace("ú","u"))
accent_normalization_dic={accent_normalization(a): a for a in list_accent}
```

1. Esta es la función para reemplazar los acentos. El parámetro (recordar que el parámetro es lo que se pasa a la función a través del argumento. Es decir, un parámetro es como un placeholder que luego recibirá un valor como argumento cuando se llame a la función), denominado "text", recibirá el argumento más adelante, el cual corresponde al input del usuario.
    - La función "accent_normalization", como su nombre lo indica, sirve para normalizar los acentos mediante la creación de un diccionario, así:

2. Recibe el argumento y le aplica los métodos .lower() para convertir todo a minúsculas y que las entradas no discrepen por cuestiones de mayúsculas.
3. Seguidamente, aplica el método .strip() para eliminar espacios innecesarios en ambos extremos de la entrada.
4. Seguidamente, si la entrada tiene una tilde, se removerá con el método .replace() anidado uno tras otro para cada vocal.
5. La última línea es una comprensión de diccionarios para crear un diccionario donde la llave (lo que está a la izquierda) sea el input sin acentos, sin espacios indeseados y en minúscula; lo que está a la derecha corresponde al valor, el cual se extrae el list_accent, que solo tiene las regiones que originalmente llevan tilde. Es decir, para cada región con tilde estoy creando una versión "desnuda" (sin tilde, sin mayúsculas y sin espacio).
    - El propósito de esto, como lo veremos más adelante, es asegurar que si el usuario ingresa un dato que debería llevar tilde, pero no se la pone, el programa lo corrija por él.

**Opciones usadas y descartadas:**
```python
#accent_normalization_dic={a.lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"): a for a in list_accent}
```

    El motivo para haber descartado esta línea es porque es repetitiva. Ya la función existe para normalizar los acentos sin tener que repetir todo otra vez en la comprensión de diccionarios.

### Validación de que el input es texto
```python
def is_input_valid(text):
    if not text:
        return False
    return text.replace(" ","").isalpha()
```

1. Esta es la segunda función del código. Como su nombre lo indica, su función es corroborar si el texto es una entrada válida, es decir, que sea texto y no contenga carácteres númericos. Debo precisar que la línea ".replace(" ","")" es absolutamente necesaria. .isalpha() rechaza todo lo que no esté catalogado como letra en la base de datos unicode, lo que incluye espacios, emojis, números, signos de puntación, carácteres especiales, etc., pero acepta todo lo que sea una letra en unicode (alfabetos no latinos, tildes, etc.). Por lo mismo, ese replace es necesario, porque necesito eliminar cualquier espacio entre palabras. Por ejemplo, si el usuario ingresa "Puerto Berrio", .isalpha() rechazará la entrada porque tiene un espacio. 
2. La función recibe un parámetros que se denomina igual al de la función anterior. Es útil porque en realidad es el mismo argumento (el input del usuario) y así me evito manejar mil nombres.
3. Si la entrada es vacía, entonces devolverá "False", de lo contrario, evaluará la entrada con .isalpha(). Si cumple, devuelve True y el código continúa, sino, devuelve False.
    - Más adelante veremos cómo se integra esta función con el código principal.

## Quinto módulo: archivo de progreso
```python
# if os.path.exists("progress_territories.json"):
#     with open ("progress_territories.json", "r") as f:
#         data_saved=json.load(f)
# else:
#     data_saved=None
```
**Explicación obsoleta de las líneas precedentes:**
1. Estas líneas son el seguro de progreso. Lo que hago aquí, con la librería os, ya integrada a Python, es tratar de crear un archivo json (el mejor para guardar listas y diccionarios), para lo cual uso la librería correspondiente, que se llame "progress_territories.json".
2. Verifico si ya existe un archivo llamado de esa manera con el método path.exists().
3. Si existe, entonces lo abro con "with open" y uso "r" como parámetro de mode. Quiere decir que lo voy a tratar como archivo de solo lectura. "as f", donde f es simplemente el "nombre" que le doy al archivo.
4. Una vez abierto, porque existe, cargo los datos a la variable "data_saved".
5. Sino existe, esa misma variable queda vacía.

**Actualización de código:**
```python
progress_root=project_root/"data"/"interim"
progress_root.mkdir(parents=True,exist_ok=True)
progress_file=progress_root/"progress_territories.json"

if progress_file.exists():
    with open(progress_file, "r") as f: #Se descartó pd.read_json(..., typ='series') para cargar el mapeo de regiones, porque el archivo es técnicamente un diccionario, no un DataFrame — pandas interpretaría las llaves como columnas y los valores como filas, sin índices reales. Es más correcto y directo usar la librería json estándar.
        raw_data_saved=json.load(f)
else:
    raw_data_saved={}
data_saved={k.strip():v for k,v in raw_data_saved.items()}
```
Más adelante se justifica la decisión de manejar el json con pathlib.

## Sexto módulo: función principal para crear el diccionario
```python
def city_territories(city_list,progress=None): #Estoy tratando de crear un diccionario con city como llave y región como valor.

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

        #territories=accent_normalization.get(territories,territories.capitalize()) #El problema es que no hay separación de datos"
        territories_key=accent_normalization(territories_raw)
        territories_processed=accent_normalization_dic.get(territories_key,territories_raw.title())


        print(f"Municipio: {c}, región: {territories_processed}")
        city_territories_dic[c]=territories_processed

    return city_territories_dic

rpoint=city_territories(city_list, progress=data_saved) #Creo el archivo para guardar la información
with open (progress_file,"w") as f:
    json.dump(rpoint,f)

#print(rpoint) esto tiene un problema, porque no me muestra realmente lo que se guardò en el json
print(json.dumps(rpoint, indent=4, ensure_ascii=False))
```

1. Esta función es el corazón del código. Funciona con dos parámetros, "city_list" y "progress".
2. Si progress (el cual se definirá más adelante) es vacío, entonces creamos un diccionario vacío con el nombre "city_territories_dic".
3. Si progress no es vacío, es decir, asumió el valor de "data_saved", como se verá más adelante, hace una copia de ese diccionario.
4. Para cada valor de city_list, ya definida previamente, verifica que no esté en el diccionario del paso anterior. Si está, el código continúa su ejecución hasta llegar a un valor que no esté.
5. Se entra en un bucle en el que se le pide al usuario que ingrese una región para cada valor de city_list solo si ese valor no está en city_territories_dic, es decir, si no está en data_saved. O que ingrese "-" para terminar. Este input se considera la entrada tal cual la escribió el usuario y por eso su nombre termina en _raw.
6. Si se ingresa, "-", la función devuelve el valor de "city_territories_dic".
7. Si se ingresa algo diferente, se activa la función para validar si es una entrada válida.
8. Además, se activa la función para normalizar la entrada. Los valores resultantes de la aplicación de esta función sobre el input se guardan en "territories_key", en oposición a "territories_raw".
9. Posteriormente, se llama al diccionario que tiene la llave normalizada para cada valor y se le dice: mire, usted va a buscar en las llaves la entrada del usuario (que recordemos que ya está normalizada), si encuentra esa llave, devuélvame el valor (el cual sí tiene las tildes y todo) y si no encuentra el valor, entonces simplemente devuélvame exactamente la entrada del usuario con inicial mayúscula.
10. Devuelvo información.
11. Añado la entrada al diccionario "city_territories_dic".
12. Acabo la función con la devolución de ese diccionario actualizado.
13. Ahora, llamo la función y aquí es donde se ejecuta el proceso ya descrito.
14. Creo el archivo json si no existe, o lo sobreescribo si existe.
15. Para comprobar la validez del archivo, lo llamo.

## Séptimo módulo: creación del archivo definitivo en una nueva ruta
1. La carpeta /data contiene 3 subcarpetas: 
    - /raw, la cual debería ser preexistente al código. En este caso, la ruta se construye como objeto con Pathlib, pero el uso de sus flags parents y exist_ok es innecesario. No está dentro del alcance del proyecto organizar un trabajo que es previo al mismo: nombrar el insumo y ubicarlo en su ruta correspondiente, sino trabajo del usuario.
    - /interim, en cambio, se maneja enteramente con Pathlib y sus flags, pues es resultado de la ejecución del código.
    - /processed contiene el output final del código: los datos limpios y procesados en un nuevo archivo.

```python
saved_output_directory=project_root/"data"/"processed"
saved_output_directory.mkdir(parents=True, exist_ok=True)
saved_file=saved_output_directory/"datos_limpios_hito1.csv"

df_territories_city.to_csv(saved_file,index=False,encoding="utf-8") #Se guarda la versión corregida: si se quisiera sobreescribr, basta con escribir el mismo nombre.
```
2. En un inicio, este código consistía solo en su última línea y usaba un str de ruta construido con ~. Ya expliqué por qué esto no era la mejor práctica.
3. Lo que conseguí con Pathlib fue: crear una ruta como objeto más flexible y, al mismo tiempo, más robusta. Pathlib, además, tiene la capacidad de crear directorios inexistentes. Las flags parents=True y exist_ok=True funcionan para eso.
    - parents puede crear carpetas en cascada si no existen desde la carpeta inicial. Por ejemplo, si "/data" no existiera, parent la crea y luego crearía "/processed".
    - exist_ok, por su parte, no genera error si la carpeta existe, pues si existe ignora el comando de creación y, si no existe, la crea.

# 02_explore_contacts.ipynb

## Primer módulo: generación del DataFrame necesario

```python
current_directory= Path.cwd()
project_root=current_directory.parent
actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"

if not actual_file.exists():
    raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")
df_contacts=pd.read_csv(actual_file)
```

1. Con lo aprendido durante el desarrollo de 01_explore_regions.ipynb, se trabajo la ruta del DataFrame inicial con pathlib, y seguí las mismas convenciones ya definidas allí.
2. ```current_directory=Path.cwd()```genera una ruta como objeto a la que le puedo aplicar los métodos de pathlib.
3. ```project_root=current_directory.parent```, por ejemplo, .parent me devuelve la ruta inmediatamente anterior a la que obtuve en el primer comando.
4. ```actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"```, aquí "/" funciona como un concatenador. project_root llega hasta ~/Escritorio/Hito1. Lo que concateno con "/" avanza desde ese primer nivel hasta llegar al archivo CSV.
5. En ```if not actual_file.exists():```compruebo la existencia del archivo (último nivel) de la línea anterior. Si el archivo no existe, que es la condición del if, raise me devuelve el error concreto y un mensaje de depuración para el usario.
6. Por último, cargo el DataFrame utilizando el nombre de la variable actual_file. Con esto consigo mayor robustez y flexibilidad en el manejo de ruta. Robustez, porque es menos probable que si alguien corre este código en su máquina reciba un error; flexibilidad, porque la ruta deja de estar tan atada a mi máquina y es más probable que funcione en una diferente.

## Segundo módulo: comprobación de datos

**Advertencia:**
Probablemente este módulo desaparecerá en main.py, pues es una comprobación que usé para determinar que el largo del DataFrame coincide con los casos identificados de consignación de los contactos en el DF original.

**Nota:**
No se eliminará, pues muestra que los casos identificados abarcan la completitud del DataFrame.

```python
nan_count=df_contacts["Contacto"].isna().sum()
empty_count=(df_contacts["Contacto"].str.strip()=="").sum()
only_number_count=df_contacts["Contacto"].str.replace(" ","").str.replace(".","").str.isdigit().sum()
anythin_else_count=(df_contacts["Contacto"].str.contains(" - | / |Cel|Correo|@", na=False).sum())
print(only_number_count+nan_count+empty_count+anythin_else_count)
```
1. Sé que el DataFrame original consiste en 135 filas.
2. Con ```nan_count=df_contacts["Contacto"].isna().sum()```compruebo la cantidad de esos valores por fila y columna específica que son NaN. (Recordar que NaN es especial: es un float que devuelve True, a diferencia de 0.0 que es un float que devuelve False. Por eso, NaN se debe comprobar de esta manera en concreta y no simplemente como si fuera un vacío, pues es su propio tipo de datos.).
3. Con ```empty_count=(df_contacts["Contacto"].str.strip()=="").sum()```compruebo la cantidad de datos efectivamente vacíos. Debo hacer strip porque una celda puede parecer vacía, pero contener espacios, que no son vacíos.
4. ```only_number_count=df_contacts["Contacto"].str.replace(" ","").str.replace(".","").str.isdigit().sum()```compruebo la cantidad de valores que son únicamente númericos. Remuevo todos los espacios con replace y preveo que no hayan número separados por puntos para más seguridad. Una vez hecho eso, con isdigit obtengo True/False para cada valor. Como True es 1 y False es 0, sum hace la sumatoria total.
5. ```anythin_else_count=(df_contacts["Contacto"].str.contains(" - | / |Cel|Correo|@", na=False).sum())```si algo no es NaN, vacío o numérico, es porque contiene otras cosas. Los casos identificados fueron: Tel único (se comprueba con la línea anterior), Correo único (cabe dentro de esta línea al no ser NaN, vacío o numérico), Tel/Correo, Tel-Correo. Estos tres últimos casos caben aquí. Si el valor contiene - o / o Cel o Correo o @, se cuenta aquí. na=false para que omita los NaN (primera línea de verificación). El operador pipe "|" funciona como la conjunción "o" en pandas.
6. El resultado: 135, esto quiere decir que no se me escapó ningun patrón.
7. El último print es evidencia del funcionamiento de la lógica que sigue. No se elimina.

## Tercer módulo: división de los valores mezclados
```python
def split_phone_email(text):
    if pd.isna(text) or not text:
        return ["Sin dato"]
    elif text.startswith("Cel:"):
        return text.replace("Cel: ","").replace("Cel:","").replace(" ","").split("Correo:")
    elif text.startswith("Correo:"):
        return text.replace("Correo:","").replace("Correo: ","").replace(" ","").split("Cel:")
    elif "/" in text:
        return text.replace(" ","").split("/")
    elif "-" in text:
        return text.replace(" ","").split("-")
    else:
        return text.split()
phone_email=df_contacts["Contacto"].apply(split_phone_email).tolist()
print(phone_email)
```
1. Esta función divide el correo del teléfono, así:
2. ```python
    if pd.isna(text) or not text:
        return ["Sin dato"]
    ```
    Si algo es NaN o vacío, la función devuelve una marca "Sin dato".
3. ```python
        elif text.startswith("Cel:"):
        return text.replace("Cel: ","").replace("Cel:","").replace(" ","").split("Correo:")
    ```
    Si el valor de la celda comienza con "Cel:", elimino esa marca en dos casos: "Cel: " y "Cel:", así evito verificar manualmente si alguno de esos casos no existe, pues me adelanto. Elimino el resto de espacios (aunque, ahora que lo pienso, debo invertir el orden para evitar el doble replace de "Cel", es decir, primero eliminar los espacios y así quedaría un solo caso "Cel:" y ningún "Cel: "). **En el código final, se hizo esta corrección.**

    Después, divido por "Correo:" (el str por el que divido no se incluye en el output).
4. ```python
    elif text.startswith("Correo:"):
        return text.replace("Correo:","").replace("Correo: ","").replace(" ","").split("Cel:")
    ```
    Mismo comentario anterior, pero con el orden inverso: remplazo "Correo" y divido por "Cel".
5. ```python
    elif "/" in text:
        return text.replace(" ","").split("/")
    elif "-" in text:
        return text.replace(" ","").split("-")
    ```
    Misma lógica de los puntos 3 y 4.
6. ```python
    else:
        return text.split()
    ```
    Esta línea es especial: es muy importante mantener la consistencia del output para que no haya posibles errores al trabajar sobre él. La naturaleza de .split() siempre devuelve una lista, por eso tengo que hacer esto, para que cualquier otro caso no me devuelva un valor que no sea lista.
7. ```python
    phone_email=df_contacts["Contacto"].apply(split_phone_email).tolist()
    ```
    Ahora, aplico esta función a la columna "Contacto" del DataFrame. Como son valores tipo serie, debo usar apply. Con tolist() convierto el output en una lista. El .tolist() es importante porque sin él, obtendría una serie. Las series son útiles para operaciones vectorizables, pero en este caso, necesito iterar valor por valor para definir si es teléfono o email según las condiciones impuestas y el problema es que los valores de la lista no son uniformes (varían en longitud, pues "row" puede contener uno o dos elementos según el caso).
8. El último print era de depuración, se eliminará.

## Cuarto módulo: definición concreta de lo que es teléfono y de lo que es correo

```python
def is_phone_email(row):
    if len(row)==1:
        if row[0].replace(" ","").isdigit():
            phone=row[0]
            email="Sin dato"
        elif "@" in row[0]:
            phone="Sin dato"
            email=row[0]
        elif row[0].replace("@","").replace("_","").replace(".","").isalnum(): #Con isalnum, en vez de isalpha, obtengo más solidez, pues los números son comunes en los correos electrónicos.
            phone="Sin dato"
            email=row[0]
        else:
            phone="Sin dato"
            email="Sin dato" #Estas líneas cambiaron para más robustez. No dependo de que salte el elif, sino que atrapo cualquier cosa que no se ajuste a los datos anteriores.
        # elif row[0]=="Sin dato":
        #     phone="Sin dato"
        #     email="Sin dato"
    else:
        if row[0].replace(" ","").isdigit():
            phone=row[0]
            email=row[1]
        elif "@" in row[0]:
            phone=row[1]
            email=row[0]
        elif row[0].replace("@","").replace("_","").replace(".","").isalnum(): #Con isalnum, en vez de isalpha, obtengo más solidez, pues los números son comunes en los correos electrónicos.
            phone=row[1]
            email=row[0]
        else:
            phone="Sin dato"
            email="Sin dato"

    return phone, email

results=[]
for row in phone_email:
    results.append(is_phone_email(row))
print (results)
```
Esto fue de lo que más me costó entender. La lógica es la siguiente:
1. En el último ciclo for itero cada elemento tipo lista de la "macrolista" phone_email generada en la función anterior.
2. Genero una nueva lista con los valores separados por correo y por teléfono. Eso es ```results.append(is_phone_email(row))```
3. Ese ```print(results)```es de depuración, se eliminará.
4. La pregunta es: ¿cómo ese ciclo for utiliza la función? Veamos.
    - La función lo que hace es tomar cada elemento y definir su longitud con len(row).
    - Si la longitud es ==1, entonces hay 3 posibilidad:
        - El contenido es "Sin dato", solo un correo o solo un teléfono.
        - Luego verifico caso por caso: si es numérico, entonces es teléfono.
        - Si no es numérico y contiene "@", entonces es correo.
        - Si no es numérico y no contiene "@" (a algún usuario se le puede pasar), entonces verifico si es alfabético, en cuyo caso es correo. Traté de introducir las cosas más comunes usadas en los correo: _,-,. (pero ahora que lo veo, también debo filtrar números, pues muchos correos se crean con números).
        - Si no es nada de lo anterior, entonces es "Sin dato".
    - Si la longitud es >1, entonces hay 3 posibilidad:
        - Si la posición inicial de la dupla dígito, entonces la segunda es correo.
        - Si la posición inicial es correo, la segunda es teléfono.
        - En cualquier otro caso, no hay datos.
        - Funciona con las mismas comprobaciones del primer caso (len==1).
5. La función devuelve teléfono y correo, exactamente en ese orden y los asigna a la lista "results" con el for ya explicado.

**Opciones usadas y descartadas:**
```python
# for element in phone_emails:
#   element.replace(" ","").replace("@","").replace(".","")

# if element.isdigit():
#   emails.append("Sin dato")
#   phones.append(element)
# elif element=="Sin dato"
#   emails.append("Sin dato")
#   phones.append("Sin dato")
```
Estas líneas tienen un problema: funcionan, pero generan offsets entre las filas del DataFrame, es decir, emparejarían teléfonos y correos con las filas no correspondiente, porque si una comprobación falla, se salta a la siguiente sin haber clasificado correctamente el valor.

## Quinto módulo: generación de dos nuevas columnas con sus valores definitivos.

```python
phone_list=[phone for phone,email in results]
email_list=[email for phone,email in results]

if "Teléfono" not in df_contacts.columns:
    df_contacts.insert(loc=4,column="Teléfono",value=phone_list)

if "Correo" not in df_contacts.columns:
    df_contacts.insert(loc=5,column="Correo",value=email_list)

if "Contacto" in df_contacts.columns:
    df_contacts.drop(columns=["Contacto"],inplace=True)

df_contacts
```
1. Utilizo comprensión de listas para generar dos listas con los valores ya clasificados.
2. Esta comprensión desempaqueta las tuplas de una vez en su orden respectivo, por eso no es necesario usar los índices que usé en la función anterior. El resultado de la función anterior ya genera un orden concreto: primero teléfono y luego correo.
3. Si la columna "Teléfono" no existe en el DataFrame, se crea en esa posición concreta con loc. Esta forma de crear columnas es inplace por defecto.
4. Lo mismo para "Correo".
5. Si la columna "Contacto" todavía existe, se elimina. Este método, por el contrario, no es inplace por defecto. Por tanto, se puede usar con seguridad para obviar valores que no quiero ver por cualquier motivo sin afectar el DataFrame original.

# 03_explore_status.ipynb

## Primer módulo: generación del DataFrame necesario

```python
current_directory= Path.cwd()
project_root=current_directory.parent
actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"

if not actual_file.exists():
    raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")
df_status=pd.read_csv(actual_file)
```
**Conocimientos importantes que salieron de este primer módulo**
1. ```df_status["Observaciones"]``` Funciona para visualizar el contenido de una sola columna, pero devuelve una Serie no renderizada en HTML para verla en estilo DataFrame. Sucede porque le estoy dando un valor tipo str, en cuyo caso "desenvuelve" los valores de la columna y me entrega una Serie.
2. ```df_status[df_status["Observaciones"]]```No funciona si pretendo utilizarla para visualizar los valores de una sola columna, devuelve KeyError. Esta sintaxis filtra y se interpreta como los valores de la columna observaciones aplicados al DataFrame original. Esos valores son una Serie, como el caso de arriba y, al ser desenvueltos, se interpretan como nombres de columnas. Al no existir esas columnas, genera error. Esta sintaxis sirve para filtrar la columna según el contenido de sus valores, pues funciona como una máscara boleana. Es decir, si aplico un filtro a esos valores, serán True/False y solo veré en el output aquellos que sea True.
3. ```df_status[["Observaciones"]]```Funciona también para visualizar los datos de una sola columna y se ve en formato DataFrame, estilo HTML. En este caso, estoy pasando una lista, por eso los corchetes dobles. No es que la lista se llame "Observaciones", sino que le estoy pidiendo que me muestre los elementos que contiene esa lista.

## Segundo módulo: patrones identificados en el DataFrame para la columna observaciones
### Primera definición de criterios:
1. "Todo normal" o "Sin novedad", siempre aparecen juntos. ("Sin novedad en el registro. Todo normal" y "Todo normal, sin novedad".). En esta categoría se incluirá tambień "Entrevista exitosa", pues en los 3 casos se implica que no hay nada que vigilar.
2. Definición de criterios urgente vs. prioritario vs. importante para el caso:
    - "Urgente" y "riesgo" son sinónimos, pues su contextos de uso connotan una afectación potencial para la vida o la salud.
    - "Prioritario" es un caso aparte, pues connota una afectación a los derechos (escolarización y firma de documentos para correcto registro). Bajo este argumento, las entradas relativas a documentos incompletos son de carácter prioritario ("Documentación incompleta").Menos grave que "urgente" (la única excepción es la entrada "Urgente: Revisar documentos faltantes", pues combina dos criterios: la urgencia y la documentación. Se tratará como "Urgente" bajo el argumento de que es una marca explícita).
    - "Importante" es el último nivel, pues no implica una afectación a la vida o a los derechos.
3. "Datos recolectados parcialmente" y "Datos incompletos por lluvia" son equivalentes.

### Patrones identificados en el DataFrame: imposición de criterios de análisis.

Los criterios que se presentan aquí tratan de responder a la pregunta sobre el propósito del DataFrame: ¿para qué se recolectan este tipo de datos? Las políticas públicas usan este tipo de datos para brindar ayuda a la población vulnerable. Puede que en un momento inicial no tengan ese propósito excplícito, pero después pueden llegar a tenerlo.

**Nota:**
*Cómo se verá más adelante, estos patrones se construyeron inicialmente a través de la identificación de palabras clave. Sin embargo, el código final se construyó con regex para abarcar más casos de los aquí mencionados.*

Así, se definen cuatro niveles:
1. Urgente: en el DataFrame, el contexto de uso de urgente aparece asociado a la palabra "riesgo". Esta categoría implica una afectación potencial a la vida o a la salud. Estado: rojo.
    - "Urgente: Riesgo de inundación detectado en el sector."
    - "Riesgo detectado en zona norte."
    - "Vivienda con fallas estructurales. Es urgente la intervención."
    - "Urgente: Revisar documentos faltantes." **(excepción: por los criterios usados, este caso pertenecería a prioritario; sin embargo, como la marca es explícita, se considerará "urgente")**.
    - Palabras clave: "urgente", "riesgo", "fallas estructurales", "falla estructural".
2. Prioritario: connota una afectación a los derechos (escolarización o documentos/datos incompletos que afecten el acceso a las políticas públicas). Estado: naranja.
    - "Documentación incompleta."
    - "Datos recolectados parcialmente."
    - "Prioritario: Familia con 5 menores sin escolarización."
    - "El habitante no se encontraba. Prioritario volver mañana."
    - "Prioritario volver mañana por firma."
    - "Datos incompletos por lluvia."
    - Palabras clave: "prioritario", "datos incompletos", "dato incompleto", "documentación incompleta", "datos recolectados parcialmente".
3. Importante: no implica una afectación a la vida o a los derechos, pero no fue una entrevista exitosa. Estado: amarillo.
    - "Importante: El informante no habla mucho."
    - "Importante: Requiere validación de linderos."
    - "Zona de difícil acceso por lluvias. Importante avisar a transporte."
    - Palabras clave: "importante".
4. Exitoso: entrevista normal, exitosa o sin novedad. Estado: verde.
    - "Sin novedad en el registro. Todo normal."
    - "Todo normal, sin novedad."
    - "Entrevista exitosa."
    - Palabras clave: "exitosa", "sin novedad", "normal".

**Consideraciones sobre el alcance:**
No es un proyecto de análisis semántico, sino de análisis de datos. No tengo las herramientas para el primer caso, por tanto, me limito al segundo a través del rastreo de palabras clave y regex.

Esta muestra contiene casos estandarizados. Validar casos como: "los datos no fueron recogidos en su totalidad" o "no se pudo realizar la visita", etc., que no se puedan definir con regex, requerirían otras herramientas de análisis semántico que aun no conozco.

**Exploración de conceptos**
*Esto no refleja el código final. Se trata de una fase exploratoria que se deja consignada porque de aquí se obtuve un gran aprendizaje.*

```python
#Aproximaciones:
#¿De verdad es necesaria una función para esto?
#status_red=df_status[(df_status["Observaciones"].str.contains("urgente|riesgo|fallas estructurales|falla estructural", case=False))]
status_red=df_status["Observaciones"].str.contains("urgente|riesgo|fallas estructurales|falla estructural", case=False)
# status_orange=df_status.loc[(df_status["Observaciones"].str.contains("prioritario|datos incompletos|dato incompleto|documentación incompleta|datos recolectados parcialmente", case=False))]
# status_yellow=df_status.loc[(df_status["Observaciones"].str.contains("importante", case=False))]
# status_green=df_status.loc[(df_status["Observaciones"].str.contains("exitosa|sin novedad|normal", case=False))]
# total_red=len(status_red)
# total_orange=len(status_orange)
# total_yellow=len(status_yellow)
# total_green=len(status_green)
# print(total_red+total_orange+total_yellow+total_green) #Output: 135, quiere decir que no se deja ningún caso por fuera.status_red=df_status.loc[(df_status["Observaciones"].str.contains("urgente|riesgo|fallas estructurales|falla estructural", case=False))]
```
Todo esto merece una explicación detallada:
1. Primera línea de código:
    - ¿Qué me devuelve?: un pandas.DataFrame
    - ¿Conserva el índice? Sí
    - Si lo convierto a lista, ¿conservaría el índice?: No
    - ¿Qué significa que me devuelva un pandas.DataFrame?: que obtengo un output en 2D, no una máscara boleana.
2. Segunda línea de código (la no comentada):
    - ¿Qué me devuelve?: un pandas.Series
    - ¿Conserva el índice?: sí
    - ¿Qué significa que me devuelva un pandas.Series?: las series también funcionan como máscaras boleanas cuando son de tipo bool **(ojo: no cualquier Series funciona como filtro, algunas son solo datos)**. Es decir, esa máscara se la puedo aplicar a un DataFrame. Ejemplo:
        ```python
        df_status.loc[status_red]
        ```
    - ¿Qué me devuelve?: un pandas.DataFrame con la máscara boleana aplicada.
3. ¿Cómo se relacionan el punto uno y dos?
    - No puedo aplicar un pandas.DataFrame a un pandas.DataFrame con .loc por cuestión de dimensiones: .loc espera algo en una dimensión para responder sí/no a algo concreto. Los DataFrame son bidimensionales, por eso el error es "Cannot index with multidimensional key".
    - df_status ya es un pandas.DataFrame y el resultado de la primera línea de código es del mismo tipo.
    - Por eso, no puedo hacer esto mismo con ```df_status.loc[status_red]```si status_red es un pandas.DataFrame, arroja error.

En conclusión: la sintaxis de las líneas comentadas es la máscara boleana ya aplicada al DataFrame original para generar un **nuevo** DataFrame filtrado. El resultado de la sintaxis no comentada no genera un nuevo DataFrame, sino que genera una **serie** que me puede servir para filtar un DataFrame.

Es importante tener en cuenta que .loc es **inplace** por defecto cuando se usa como asignador .loc[máscara,"Estado"]=x, si se usa como lector .loc[máscara], el DataFrame original queda intacto.

**Código definitivo: regex y máscara boleana**

```Python
fil_red=df_status["Observaciones"].str.contains(r"urgente|riesgo|fall[ao]s?\b\s*estructural[e]?s?\b",case=False)
fil_orange=df_status["Observaciones"].str.contains(r"prioritario|incomplet[ao]?s?\b|recolec\w*\b.*parcial\w*\b",case=False)
fil_yellow=df_status["Observaciones"].str.contains("important", case=False)
fil_green=df_status["Observaciones"].str.contains(r"[ée]xito[s]?[oa]?|sin novedad|normal", case=False)

print(fil_red.sum()+fil_orange.sum()+fil_yellow.sum()+fil_green.sum())
```
*Estas líneas son la versión con regex de las que se usaron y fueron descartadas (ver más arriba).*

1. fil_red incluye los strings literales "urgente" y "riesgo". Para los demás casos, se usa regex, así:
    - ```fall[ao]s?\b\s*estructural[e]?s?\b```significa: la coincidencia literal "fall" seguida de "a" u "o", seguida de una "s" opcional, fin de palabra y cualquier cantidad de espacios antes de la coincidencia literal "estructural" seguida de una "e" opcional, seguida de una "s" opcional, fin de palabra. Eso permite casos como "falla estructural", "fallas estructurales", "fallo estructural", "fallos estructurales", "fallo estructurales", "falla estructurales", "falla estructurals", etc.
2. file_orange incluye el string literal "prioritario". Para los demás casos, se usa regex, así:
    - ```incomplet[ao]?s?\b```significa: la coincidencia literal "incomplet" seguida de "a" u "o", seguido de una "s" opcional, fin de palabra. Eso encuentra cosas como "incompleta", "incompleto", "incompletas", "incompletos".
    - ```recolec\w*\b.*parcial\w*\b```significa: la coincidencia exacta "recolec" seguida de cualquier carácter admitido por \w (dígitos, letras mayúscuas o minúsculas con o sin tilde) cualquier cantidad de veces, fin de palabra. Eso abarca cosas como "recolecta", "recolectados", "recolección", "recolectando", "recolectar", etc. Eso seguido de cualquier carácter cualquier cantidad de veces, seguido de la coincidencia exacta "parcial", seguido de cualquier carácter admitido por \w cualquier cantidad de veces, fin de palabra. Con eso puedo abarcar desde "recolectados parcialmente" hasta "recolectando de forma parcial".
3. fil_yellow incluye el string literal "important" y no necesito nada más, porque ese es un substring de todas las palabras importantes en este caso: importante, importantes, etc. Nota aparte: se verificó que "important" (sin la "e" final) no genera falsos positivos con palabras como "importación" o "importador" (que sí coincidirían con el prefijo más corto "import"), a diferencia de lo que se podría pensar. Este hallazgo no fue el motivo original para usar "important" — fue una corrección de un error de tipeo —, pero es una propiedad útil del patrón que vale la pena dejar registrada para el futuro.
4. fil_green incluye los strings literales "sin novedad" y "normal". Para los demás casos, se usa regex, así:
    - ```[ée]xito[s]?[oa]?```significa: "é" o "e" seguida del string literal "xito" seguida de una "s" opcional, seguida de "o" o "a" opcional. Así abarco palabras clave como "éxito" ("datos recolectados con éxito"), "exitosa" ("entrevista exitosa"), "exitoso" ("encuentro exitoso").
5. La última línea, el print, me sirve para tener un conteo de la cantidad de casos que estoy abarcando con esto: todo esto me da 135, que es justo el largo de DataFrame. Quiere decir que no estoy dejando casos por fuera.

## Tercer módulo: generación del DataFrame con la nueva columna "Estado"

```python
df_status["Estado"] = pd.NA

df_status.loc[fil_red,"Estado"]="Rojo"
df_status.loc[fil_orange,"Estado"]="Naranja"
df_status.loc[fil_yellow,"Estado"]="Amarillo"
df_status.loc[fil_green,"Estado"]="Verde"
df_status
```
1. La primera línea es profiláctica: si la columna no existe, la crea y asigna todos sus valores a NaN. Si ya existe, ajusta todos sus valores a NaN. ¿Por qué? Porque si hay un cambio en el código anterior, puede que algunos casos entren y otros salgan de la máscara boleana, es decir, que cambien de estado: lo que era True se haga False y viceversa. .loc solo trabaja sobre lo True y lo False permanece igual. Entonces, todo lo que se volvió False y antes era True, se conservaría tal cual. Es decir, quedarían filtros aplicados de iteraciones pasadas. Si cada vez que ejecuto el código vuelvo todo NaN, omito ese problema.
2. Aplico la máscara boleana al DataFrame por cada estado. Al final, obtengo un solo DataFrame con las máscaras aplicadas.

## Cuarto módulo: reordenamiento de columnas

```Python
first_cols=[col for col in df_status.columns if col not in ["Observaciones","Estado"]]
new_order=first_cols+["Observaciones","Estado"]
df_status=df_status[new_order]
df_status
```
1. Genero una lista que contiene las columnas que no son ni "Observaciones" ni "Estado" (justo las dos columnas que quiero dejar para el final del DataFrame).
2. Genera una nueva lista con el orden deseado: primero las columnas que no son "Observaciones" ni "Estado" y después estas dos.
3. Para que el cambio sea efectivo, debo hacer que el DataFrame original sea igual al DataFrame original con el orden cambiado. 

Esta sintaxis me ahorra escribir cada columna en el orden deseado: ```df_status["A","B","C","Observaciones","Estado"]```

# 04_explore_names-dates.ipynb

## Primer módulo: generación del DataFrame necesario

```python
current_directory= Path.cwd()
project_root=current_directory.parent
actual_file=project_root/"data"/"raw"/"datos_sucios_hito1.csv"

if not actual_file.exists():
    raise FileNotFoundError("Falta el insumo de trabajo. Debe nombrarlo como \"datos_sucios_hito1.csv\" y guardarlo en data/raw/")
df_namedates=pd.read_csv(actual_file)
df_namedates
```
## Segundo módulo: normalización de nombres

```python
names_nodata=df_namedates["Nombre_Informante"].isna()|(df_namedates["Nombre_Informante"].str.replace(" ","")=="")|(df_namedates["Nombre_Informante"].str.contains("N/A",case=False))|(df_namedates["Nombre_Informante"].str.contains("No registra",case=False))
df_namedates.loc[names_nodata,"Nombre_Informante"]="Sin dato"

names_data=df_namedates["Nombre_Informante"]!="Sin dato"
df_namedates.loc[names_data,"Nombre_Informante"]=df_namedates.loc[names_data,"Nombre_Informante"].str.title()
df_namedates
```
1. names_nodata es una máscara boleana que luego se aplica a df_namesdata para que, todo lo que sea True en esa máscara, pase a ser "Sin dato". Por eso, la máscara incluye valores NaN, o valores que después de eliminar los espacios quedan vacíos, o valores "N/A" o "No registra".
    - ```(df_namedates["Nombre_Informante"].str.replace(" ","")=="")```esta condición de la línea es particularmente interesante: nótese que todo lo demás devuelve un boleano, pero replace no devuelve boleano, sino str. Por eso debo incluir =="", lo que lo convierte en esto: ¿después de eliminar los espacios, lo que queda es igual a vacío? Esa respuesta si es boleana.
2. Aplico esa máscara boleana a df_namedates y, como dije, todo lo que es True ahora es "Sin dato".
3. Luego defino otra máscara names_data, la cual consiste en todos los valores que sean diferentes a "Sin dato".
4. Esa máscara la aplico a df_namedates para que a todo lo que sea diferente a "Sin dato" se le aplique .title. De esa manera, no queda "Sin Dato" y los nombres quedan con sus respectivas mayúsculas.
5. La línea df_namedates solo la usé para ver el resultado. No quedará en main.py

**Código usado y descartado:**

```python
# for name in names:
#     if pd.isna(name):
#         name="Sin dato"
#     elif name.replace(" ","")=="":
#         name="Sin dato"

#     names_lower.append(name.lower())

# print(names_lower)
```
**¿Por qué se descartó**
Porque el código anterior, si bien funciona (no está terminado, lo abandoné antes de terminarlo) es una forma complicada de hacer lo que deseo: filtar NaN y vacíos y pasar todo a minúsculas. Es una operación vectorizable que puedo realizar en el DataFrame directamente a través de máscaras boleanas.

## Tercer módulo: normalizar fechas (patrón de letras a números)

```python
months_map = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

def numeric_month(match):
    text_month=match.group("month")
    return f"{match.group("day")}/{months_map[text_month]}/{match.group("year")}"

df_namedates["Fecha_Registro"]=df_namedates["Fecha_Registro"].str.replace(r"(?P<month>\w{3})\s*(?P<day>\d{2}),\s*(?P<year>\d{2,4})",numeric_month,regex=True)
df_namedates[["Fecha_Registro"]]
```
1. Defino un diccionario que me permitirá mapear los meses. En este diccionario, la llave es el mes y el valor es su número correspondiente.
2. Defino una función recibe como argumento el match que extraigo con regex, así:
    - ```df_namedates["Fecha_Registro"]=df_namedates["Fecha_Registro"].str.replace(r"(?P<month>\w{3})\s*(?P<day>\d{2}),\s*(?P<year>\d{2,4})",numeric_month,regex=True)```esta línea dice: encuentre 3 letras consecutivas y agrúpelas bajo el nombre "month", seguidas de cualquier cantidad de espacios, seguidos de dos dígitos consecutivos agrupados bajo el nombre "day", seguidos de coma y cualquier cantidad de espacios, seguidos de 2 o 4 dígitos consecutivos agrupados bajo el nombre "year".
    - Ese patrón, lo va a reemplazar (aunque lo correcto sería decir "reordenar en este caso) según lo que devuelva la función.
3. La función le asigna a una variable text_month el nombre del mes capturado con regex. Es decir, las 3 letras consecutivas.
4. La función devuelve el grupo "day"/el valor para la llave text_month/el grupo "year".
5. La línea df_namedates[["Fecha_Registro"]] solo la usé para visualizar. No se compila en main.py.

## Cuarto módulo: normalizar fechas en orden día/mes/año

```python
#df_namedates["Fecha_Registro"].str.extract(r"(?P<a>\d{2,4})[-/](?P<b>\d{2})[-/](?P<c>\d{2,4})")

def month_year_date(match):
    #Por consistencia del DataSet y el contexto de uso, se asume que la posición b siempre es mes.
    # if len(match.group("a"))==2 and match.group("a")>12:
    #     return f"{match.group("a")}/{match.grouo("b")}/{match.group("c")}" #La primera posición puede ser año, mes o día. Si tiene 2 digítos y es mayor a 12, es día, en cuyo caso la segunda posición solo puede ser mes y la tercera año (pues, año nunca aparece en el medio).
    if len(match.group("a"))==2: 
        return f"{match.group("a")}/{match.group("b")}/{match.group("c")}" #Esta condición resume la primera posición. Si tiene dos dígitos, se asume SIEMPRE que es día por la consistencia de los datos, pues incluso si es igual o menor a 12, es imposible saber si es mes o día. Pero, además, el patrón Mes-Día-Año no se usa en el contexto de este DataSet.
    #elif len(match.group("a"))==4 and int(match.group("b"))<=12: #Lo que viene después del "and" sobra: es una medida de seguridad que NO determina si en el medio hay un mes o un día, pero que puede reducir el riesgo de que se trate de un día. Sin embargo, sobra, es sobreingeniería, porque el patrón Año-Día-Mes no se usa.
    else:
        return f"{match.group("c")}/{match.group("b")}/{match.group("a")}"

df_namedates["Fecha_Registro"]=df_namedates["Fecha_Registro"].str.replace(r"(?P<a>\d{2,4})[-/](?P<b>\d{2})[-/](?P<c>\d{2,4})",month_year_date,regex=True)
df_namedates
```
**Nota:**omitir lo que está comentado, pues el código final no lo tiene. Los comentarios se dejan para discernir el proceso de razonamiento detrás de este código.

No es necesaria una explicación, pues este módulo funciona de manera similar al anterior.

# Oportunidades de mejora
1. ¿Qué pasa si el usuario a una región le pone una tilde que no lleva?