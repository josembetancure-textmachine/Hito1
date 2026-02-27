# README HITO 1

## Organizar el archivo
### Municipio y región
Se ha detectado que los municipios no se corresponden con sus regiones \(Bajo Cauca, Urabá y Nordeste, todas en Antioquia\). Por este motivo, el primer paso es arreglar los municipios por cada región.
1. Definir una función que tome la región y sus municipios y cree un diccionario con esta información. La llave será el municipio y el valor la región para mantener una relación O\(1\)
2. Esta función "recorrerá" la columna de municipios y con eso cambiará el valor de la región por el correspondiente.
### Contactos
Se ha detectado que las celdas de contacto comparten correo electrónico y teléfono. Por este motivo, se deben separar en dos columnas independientes.
1. Definir una función que recorra las celdas de esta columna para separar sus elementos y guardarlos en variables.
2. Asignar cada variable a su nueva columna respectiva por fila.
### Observaciones
Se deben definir los estados en una nueva columna basados en las observaciones.
1. Si la observación contiene términos como "riesgo" o "urgente", su estado será rojo.
2. Para términos como "prioritario" o "importante", el estado será naranja.
3. Para los demás términos, el estado será verde.
4. Por orden, la columna de observaciones y la columna de estado se situarán al final de la tabla.
### Fechas y nombres
Normalizar los valores.
1. Todas las fechas deben quedar en el mismo formato.
2. Todos los nombres deben quedar escritos con mayúscula inicial para cada nombre y cada apellido.

