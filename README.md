# Tarjetas_v4
Parsea archivos PDF de liquidaciones mensuales de tarjetas Visa, Cabal y Maestro (débito únicamente)

## Librerías necesarias
* sqlite3
* time
* glob
* re
* datetime

## Uso básico
### Primer inicio
Crear la base de datos (data.db) con el siguiente statement:
```
CREATE TABLE operaciones
    (sucursal char, fpago float, liqno int, lote int,
    arancel float, impuestos float, importe float,
    adicionales float, tarjeta char);
```
### Mensualmente
1. Descargar las liquidaciones mensuales en PDF desde las páginas correspondientes ([Prisma](http://www.prismamediosdepago.com.ar/) para Visa y Cabal, [FirstData](https://www.firstdata.com.ar/) para Maestro).
2. Guardar esas liquidaciones en una carpeta ./pdf, en el mismo directorio que todos los fuentes.
3. Ejecutar ```importar.bat```.
4. (Opcional) Ejecutar ```reporte.bat```. Esto crea un archivo export.csv que puede ser usado con Excel para visualizar los datos de manera más cómoda
