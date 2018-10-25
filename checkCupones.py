import csv
import sqlite3 as sql
import datetime as dt
import time
import os

class cupones():
  db = None

  def __init__(self):
    self.db = sql.connect('data.db')
    
  def getInput(self):
    result = []
    print('### INICIO ###')
    syear = input('\tAño: ')
    smonth = input('\tMes: ')
    sday = input('\tDia: ')

    print('\n###  FIN  ###')
    fyear = input('\tAño: ')
    fmonth = input('\tMes: ')
    fday = input('\tDia: ')

    try:
      result.append(time.mktime(time.strptime('%s-%s-%s' % (syear, smonth, sday), r'%Y-%m-%d')))
      result.append(time.mktime(time.strptime('%s-%s-%s' % (fyear, fmonth, fday), r'%Y-%m-%d')))
    except:
      result = []
    
    return result

  def quit(self):
    self.db.commit()
    self.db.close()
  
  def importCupones(self):
    sql_insert_str = 'INSERT INTO C_Cupones (fecha, local, tarjeta, lote, importe) VALUES (?,?,?,?,?)'
    
    with open('Cupones.csv', 'rt') as cf:
      r = csv.DictReader(cf, delimiter=';')
      for row in r:
        d = dt.datetime.strptime(row['Fecha'], r'%d/%m/%Y').timestamp()
        money = float(row['Importe'].replace('.', '').replace(',', '.'))
        self.db.execute(sql_insert_str, (d, row['Local'].lower(), row['Tarjeta'].lower(), row['Lote'], money))
      cf.close()
      self.db.commit()

  def getNoPagados(self):
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

    cur = self.db.execute(sql_lotes_no_pagos).fetchall()

    return cur

  def getLiquidados(self):
    fechas = []
    while (fechas == []):
      fechas = self.getInput()

    sql_lotes_liquidados = '''
    CREATE TABLE C_Export AS SELECT * FROM
    (
      SELECT DATE(c.fecha, 'unixepoch') AS fpres, o.sucursal,
      o.tarjeta, o.lote, o.fpago, o.liqno, c.importe, o.recibido,
      (c.importe - o.recibido) AS diff,
      o.gasto, (o.recibido - o.gasto) AS liquidado FROM C_Cupones c
      INNER JOIN 
      (
        SELECT sucursal, lote, fpago as unfp, DATE(fpago, 'unixepoch') AS fpago, liqno, tarjeta,
        SUM(importe) AS recibido, SUM(arancel + impuestos + adicionales) AS gasto
        FROM operaciones
        GROUP BY sucursal, tarjeta, lote
      ) o
      ON c.local == o.sucursal AND c.lote == o.lote AND c.tarjeta == o.tarjeta
      WHERE o.unfp BETWEEN %s AND %s
    );
    ''' % (fechas[0], fechas[1])

    self.db.execute(sql_lotes_liquidados)

    sql_lotes_liquidados = '''
    SELECT *, (liquidado - gto_bco) AS neto FROM
    (
      SELECT *, (liquidado * .006) AS gto_bco FROM C_Export
    );
    '''

    cur = self.db.execute(sql_lotes_liquidados).fetchall()

    sql_lotes_liquidados = '''DROP TABLE C_Export;'''

    self.db.execute(sql_lotes_liquidados)

    return cur

  def printNoPagados(self):
    cur = self.getNoPagados()
    n = len(cur)
    i = 0
    print('%-20s | %-10s | %-8s' % ('Sucursal', 'Tarjeta', 'Lote'))
    print('-' * 44)
    while (i < n):
      print('%20s | %10s | %8s' % (cur[i][1], cur[i][2], cur[i][3]))
      i += 1

  def writeQuery(self, qtype = 0):
    cur = []
    if qtype == 1:
      cur = self.getNoPagados()
    elif qtype == 2:
      cur = self.getLiquidados()
    
    with open('export.csv', 'wt') as fp:
      for row in cur:
        for cell in row:
          fp.write((str(cell) + ';').replace('.', ','))
        fp.write('\n')
      fp.close()
    
    os.system('start export.csv')

def printOpciones():
  print('Tipo de reporte:')
  print('\t1. Cupones no pagados a la fecha')
  print('\t2. Cupones liquidados a la fecha\n')
  return int(input('Que reporte desea? (1-2): '))

if __name__ == '__main__':
  cp = cupones()

  choice = 0
  while not (1 <= choice and choice <= 2):
    choice = printOpciones()

  cp.writeQuery(choice)
  cp.quit()
