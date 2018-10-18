# Tarjetas_v4
Parsea archivos PDF de liquidaciones mensuales de tarjetas Visa, Cabal y Maestro (débito únicamente)

## Librerías necesarias
* sqlite3
* time
* glob
* re
* datetime

## Statement para crear la DB en SQLite3
```
CREATE TABLE operaciones
    (sucursal char, fpago float, liqno int, lote int,
    arancel float, impuestos float, importe float,
    adicionales float, tarjeta char);
```
