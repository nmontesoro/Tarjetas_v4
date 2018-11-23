# Tarjetas_v4
Parsea archivos PDF de liquidaciones mensuales de tarjetas Visa, Cabal y Maestro (débito únicamente).

## Librerías necesarias
* PyPDF2
```shell
pip install pypdf2
```

## Uso básico
### Primer inicio
Crear la base de datos (data.db) con el siguiente statement:
```sql
CREATE TABLE "cupones" 
    ( `fecha` INTEGER, `sucursal` TEXT, `tarjeta` TEXT, `lote` INTEGER,
    `importe` REAL );

CREATE TABLE operaciones
    (sucursal char, fpago float, liqno int, lote int, arancel float,
    impuestos float, importe float, adicionales float, tarjeta char);

CREATE VIEW cupones_agrupados AS
SELECT sucursal, tarjeta, lote, SUM(importe) AS importe
FROM cupones
GROUP BY sucursal, tarjeta, lote;

CREATE VIEW lotes_agrupados AS
SELECT sucursal, tarjeta, lote, GROUP_CONCAT(DISTINCT liqno) AS liquidaciones,
    SUM(importe) AS importe,
    SUM(arancel + impuestos + adicionales) AS gastos
FROM operaciones
GROUP BY sucursal, tarjeta, lote;

CREATE VIEW export AS
SELECT c.sucursal, c.tarjeta, c.lote, l.liquidaciones, c.importe AS presentado,
    l.importe AS liquidado, (l.importe - c.importe) AS diferencia, l.gastos
FROM cupones_agrupados c
LEFT JOIN lotes_agrupados l
ON c.sucursal == l.sucursal
    AND c.tarjeta == l.tarjeta
    AND c.lote == l.lote;
```
### Mensualmente
1. Cargar los cupones de liquidaciones desde un archivo `Cupones.csv`, con formato `fecha|sucursal|tarjeta|lote|importe`.
    * Usar `importarCupones.py`, modificando el separador y los caracteres a reemplazar si la configuración regional lo requiriera.
1. Borrar todos los PDF que hayan quedado de fechas anteriores.
2. Descargar las liquidaciones mensuales en PDF desde las páginas correspondientes ([Prisma](http://www.prismamediosdepago.com.ar/) para Visa y Cabal, [FirstData](https://www.firstdata.com.ar/) para Maestro).
3. Guardar esas liquidaciones en una carpeta ./pdf, en el mismo directorio que todos los fuentes.

   **Importante:** Los nombres deben respetar el formato `YYYY-MM-(tarjeta)-(sucursal).pdf`. Por ejemplo, `2018-08-Maestro-Belgrano.pdf`.

4. Ejecutar `importfrompdf.py`.
5. *(Opcional)* Ejecutar `DBtoCSV.py`. Esto crea los archivos `pagados.csv`, `nopagados.csv` y `problematicos.csv`, que pueden ser usados con Excel para visualizar los datos de manera más cómoda.
