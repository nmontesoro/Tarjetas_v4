import csv
import sqlite3 as sql
import datetime as dt

db = sql.connect('data.db')
db.execute('CREATE TABLE C_Cupones (fecha float, local char, tarjeta char, lote int)')

sql_insert_str = 'INSERT INTO C_Cupones (fecha, local, tarjeta, lote) VALUES (?,?,?,?)'
with open('Cupones.csv', 'rt') as cf:
  r = csv.DictReader(cf, delimiter=';')
  for row in r:
    d = dt.datetime.strptime(row['Fecha'], r'%d/%m/%Y').timestamp()
    db.execute(sql_insert_str, (d, row['Local'].lower(), row['Tarjeta'].lower(), row['Lote']))
  cf.close()

sql_lotes_no_pagos = '''SELECT c.*, o.* FROM C_Cupones c
                        LEFT JOIN operaciones o
                        ON c.lote == o.lote AND c.local == o.sucursal AND c.tarjeta == o.tarjeta
                        WHERE o.fpago IS NULL;'''
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