'#1.
df_territories_city=pd.read_csv("./datos_sucios_hito1.csv")
#2.
city_list=df_territories_city["Municipio"].unique().tolist()
#3.
df_territories_accent=df_territories_city[df_territories_city["Región"].str.contains("á|é|í|ó|ú",case=False)]
df_accent=df_territories_accent["Región"].unique().tolist()
df_accent'

1. La línea de pandas que uso para abrir el archivo que contiene los datos. El "." significa la ruta actual. pd es el acortamiento universal para pandas cuando lo importo como "import pandas as pd".
2.  Aquí genero una lista a partir del dataframe original. Con los métodos unique() solo obtengo los valores únicos de la columna "Municipio". Esto es útil para que el programa no me pida un municipio todas las veces que aparezca. Con tolist(), convierto todo en lista de una vez.
3. Los usuarios son expertos en no usar tildes, pero el manejo de datos precisos las requiere. Una tilde puede distinguir dos conceptos distintos entre sí. Por eso genero un dataframe, a partir del original, que contenga únicamente las regiones (que finalmente serán el input del usuario) que tienen tilde. Es importante notar la sintaxis: esto es una máscara booleana. A simple vista, parece redundante, pero tiene un sentido lo que está dentro de corchetes es el filtro que se aplica a lo que esta fuera. Es muy explícito. Uno podría aplicar un filtro con los datos de una Tabla A a una Tabla B. Es raro, pero posible.

Otras opciones usadas y descartadas:
city_columns=["Municipio"]
df_city=pd.read_csv("./datos_sucios_hito1.csv",usecols=city_columns)
df_city

2. Opción ganadora por eficiencia de recursos
df_city=df_territories_city[["Municipio"]]
df_city

Esta última opción la descarté, sin embargo, porque agrega un paso innecesario a esto, pues desde el principio puedo crear la lista directamente.

Consideraciones:
df_accent y df_city deben cambiar de nombre por list_accent y list_city pues, en realidad son listas.

def accent_normalization(text):
    return (text.lower().strip()
            .replace("á","a")
            .replace("é","e")
            .replace("í","i")
            .replace("ó","o")
            .replace("ú","u"))
accent_normalization_dic={accent_normalization(a): a for a in df_accent}

Esta es la función para reemplazar los acentos. El parámetro (recordar que el parámetro es lo que se pasa a la función a través del argumento. Es decir, un parámetro es como un placeholder que luego recibirá un valor como argumento cuando se llame a la función), denominado "text", recibirá el argumento más adelante, el cual corresponde al input del usuario.

La función "accent_normalization", como su nombre lo indica, sirve para normalizar los acentos mediante la creación de un dicción, así:

1. Recibe el argumento y le aplica los métodos .lower() para convertir todo a minúsculas y que las entradas no discrepen por cuestiones de mayúsculas.
2. Seguidamente, aplica el método .strip() para eliminar espacios innecesarios en ambos extremos de la entrada.
3. Seguidamente, si la entrada tiene una tilde, se removerá con el método .replace() anidad uno tras otro para cada vocal.
4. La última línea es una comprensión de diccionarios para crear un diccionario donde la llave (lo que está a la izquierda) sea el input sin acentos, sin espacios indeseados y en minúscula; lo que está a la derecha corresponde al valor, el cual se extrae el df_accent, que solo tiene las regiones que originalmente llevan tilde. Es decir, para cada región con tilde estoy creando una versión "desnuda" (sin tilde, sin mayúsculas y sin espacio).

El propósito de esto, como lo veremos más adelante, es asegurar que si el usuario ingresa un dato que debería llevar tilde, pero no se la pone, el programa lo corrija por él.

Opciones usadas y descartadas:
#accent_normalization_dic={a.lower().strip().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"): a for a in df_accent}
El motivo para haber descartado esta línea es porque es repetitiva. Ya la función existe para normalizar los acentos sin tener que repetir todo otra vez en la comprensión de diccionarios.

def is_input_valid(text):
    if not text:
        return False
    return text.replace(" ","").isalpha()

Esta es la segunda función del código. Como su nombre lo indica, su función es corroborar si el texto es una entrada válida, es decir, que sea texto y no contenga carácteres númericos. Debo precisar que la línea ".replace(" ","")" es absolutamente necesaria. .isalpha() rechaza todo lo que no esté catalogado como letra en la base de datos unicode, lo que incluye espacios, emojis, números, signos de puntación, carácteres especiales, etc., pero acepta todo lo que sea una letra en unicode (alfabetos no latinos, tildes, etc.). Por lo mismo, ese replace es necesario, porque necesito eliminar cualquier espacio entre palabras. Por ejemplo, si el usuario ingresa "Puerto Berrio", .isalpha() rechazará la entrada porque tiene un espacio. 

1. La función recibe un parámetros que se denomina igual al de la función anterior. Es útil porque en realidad es el mismo argumento (el input del usuario) y así me evito manejar mil nombres.
2. Si la entrada es vacía, entonces devolverá "False", de lo contrario, evaluará la entrada con .isalpha(). Si cumple, devuelve True y el código continúa, sino, devuelve False.

Más adelante veremos cómo se integra esta función con el código principal.

if os.path.exists("progress_territories.json"):
    with open ("progress_territories.json", "r") as f:
        data_saved=json.load(f)
else:
    data_saved=None

Estas líneas son el seguro de progreso. Lo que hago aquí, con la librería os, ya integrada a Python, es tratar de crear un archivo json (el mejor para guardar listas y diccionarios), para lo cual uso la librería correspondiente, que se llame "progress_territories.json".

1. Verifico si ya existe un archivo llamado de esa manera con el método path.exists().
2. Si existe, entonces lo abro con "with open" y uso "r" como parámetro de mode. Quiere decir que lo voy a tratar como archivo de solo lectura. "as f", donde f es simplemente el "nombre" que le doy al archivo.
3. Una vez abierto, porque existe, cargo los datos a la variable "data_saved".
4. Sino existe, esa misma variable queda vacía.

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

        territories_key=accent_normalization(territories_raw)
        territories_processed=accent_normalization_dic.get(territories_key,territories_raw.title())


        print(f"Municipio: {c}, región: {territories_processed}")
        city_territories_dic[c]=territories_processed

    return city_territories_dic

rpoint=city_territories(city_list, progress=data_saved)
with open ("progress_territories.json","w") as f:
    json.dump(rpoint,f)

print(json.dumps(rpoint, indent=4, ensure_ascii=False))

Esta función es el corazón del código. Funciona con dos parámetros, "city_list" y "progress".

1. Si progress (el cual se definirá más adelante) es vacío, entonces creamos un diccionario vacío con el nombre "city_territories_dic".
2. Si progress no es vacío, es decir, asumió el valor de "data_saved", como se verá más adelante, hace una copia de ese diccionario.
3. Para cada valor de city_list, ya definida previamente, verifica que no esté en el diccionario del paso anterior. Si está, el código continúa su ejecución hasta llegar a un valor que no esté.
4. Se entra en un bucle en el que se le pide al usuario que ingrese una región para cada valor de city_list solo si ese valor no está en city_territories_dic, es decir, si no está en data_saved. O que ingrese "-" para terminar. Este input se considera la entrada tal cual la escribió el usuario y por eso su nombre termina en _raw.
5. Si se ingresa, "-", la función devuelve el valor de "city_territories_dic".
6. Si se ingresa algo diferente, se activa la función para validar si es una entrada válida.
7. Además, se activa la función para normalizar la entrada. Los valores resultantes de la aplicación de esta función sobre el input se guardar en "territories_key", en oposición a "territories_raw".
8. Posteriormente, se llama al diccionario que tiene la llave normalizada para cada valor y se le dice: mire, usted va a buscar en las llaves la entrada del usuario (que recordemos que ya está normalizada), si encuentra esa llave, devuélvame el valor (el cual sí tiene las tildes y todo) y si no encuentra el valor, entonces simplemente devuélvame exactamente la entrada del usuario con inicial mayúscula.
9. Devuelvo información.
10. Añado la entrada al diccionario "city_territories_dic".
11. Acabo la función con la devolución de ese diccionario actualizado.
12. Ahora, llamo la función y aquí es donde se ejecuta el proceso ya descrito.
12. Creo el archivo json si no existe, o lo sobreescribo si existe.
13. Para comprobar la validez del archivo, lo llamo.