from pdfparser import PdfParser
import glob
import sqlite3 as sql

db = sql.connect('data.db')
for file in glob.glob('pdf/*.pdf'):
    print('Procesando %s' % (file))
    p = PdfParser(file)
    liqs = p.get_liquidaciones()

    sql_insert_str = ('INSERT INTO operaciones (sucursal, fpago, liqno, lote, '
        + 'arancel, impuestos, importe, adicionales, tarjeta)'
        + ' VALUES (?,?,?,?,?,?,?,?,?)')
    suc = p.sucursal
    tar = p.tarjeta
    for liq in liqs:
        db.execute(sql_insert_str, (suc, liq['fpago'], liq['liqno'],
                                    liq['lote'], liq['arancel'],
                                    liq['impuestos'], liq['importe'],
                                    liq['adicionales'], tar))
    db.commit()

db.close()
