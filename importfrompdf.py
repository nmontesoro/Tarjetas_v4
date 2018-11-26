from pdfparser import pdfParser
import glob
import sqlite3 as sql

db = sql.connect('data.db')
for file in glob.glob('pdf/*.pdf'):
    print('Procesando %s' % (file))
    p = pdfParser(file)
    liqs = p.getLiquidaciones()

    sql_insert_str = 'INSERT INTO operaciones (sucursal, fpago, liqno, lote, '
    + 'arancel, impuestos, importe, adicionales, tarjeta)'
    + ' VALUES (?,?,?,?,?,?,?,?,?)'
    suc = p.sucursal
    tar = p.tarjeta
    for liq in liqs:
        db.execute(sql_insert_str, (suc, liq['fpago'], liq['liqno'],
                                    liq['lote'], liq['arancel'],
                                    liq['impuestos'], liq['importe'],
                                    liq['adicionales'], tar))
    db.commit()

db.close()
