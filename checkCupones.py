import csv
import sqlite3 as sql
import datetime as dt

def printCupones():
  db = sql.connect('data.db')
  db.execute('CREATE TABLE C_Cupones (fecha float, local char, tarjeta char, lote int, importe float)')

  sql_insert_str = 'INSERT INTO C_Cupones (fecha, local, tarjeta, lote, importe) VALUES (?,?,?,?,?)'
  with open('Cupones.csv', 'rt') as cf:
    r = csv.DictReader(cf, delimiter=';')
    for row in r:
      d = dt.datetime.strptime(row['Fecha'], r'%d/%m/%Y').timestamp()
      money = float(row['Importe'].replace('.', '').replace(',', '.'))
      db.execute(sql_insert_str, (d, row['Local'].lower(), row['Tarjeta'].lower(), row['Lote'], money))
    cf.close()

  sql_lotes_no_pagos = '''SELECT DATE(c.fecha, 'unixepoch') AS fecha, c.local,
                            c.tarjeta, c.lote, c.importe AS bruto
                          FROM C_Cupones c
                          LEFT JOIN
                          (
                            SELECT sucursal, lote, fpago, tarjeta
                            FROM operaciones
                            GROUP BY sucursal, tarjeta, lote
                          ) o
                          ON c.lote == o.lote AND c.local == o.sucursal AND c.tarjeta == o.tarjeta
                          WHERE o.fpago IS NULL
                          ORDER BY c.local, c.tarjeta;'''
  cur = db.execute(sql_lotes_no_pagos).fetchall()

  n = len(cur) 
  i = 0
  print('%-20s | %-10s | %-8s' % ('Sucursal', 'Tarjeta', 'Lote'))
  print('-' * 44)
  while (i < n):
    print('%20s | %10s | %8s' % (cur[i][1], cur[i][2], cur[i][3]))
    i += 1

  db.execute('DROP TABLE C_Cupones')
  db.commit()
  db.close()

if __name__ == '__main__':
  printCupones()
