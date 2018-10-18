import sqlite3 as sql
import time

def getInput():
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

usrin = getInput()
while (len(usrin) == 0):
  print('Error en el rango de fechas. Pruebe nuevamente...\n\n')
  usrin = getInput()

db = sql.connect('data.db')
sql_select_str = '''SELECT sucursal, date(fpago, 'unixepoch') as fecha, tarjeta, liqno, lote,
                    importe as bruto, (arancel + impuestos + adicionales) as gastos,
                    (importe - (arancel + impuestos + adicionales)) as liquidado
                    FROM operaciones
                    WHERE fpago BETWEEN %s AND %s;''' % (usrin[0], usrin[1])

rows = db.execute(sql_select_str)
bytes_written = 0
e_filename = 'export.csv'
with open(e_filename, 'wt') as fp:
  for row in rows:
    for cell in row:
      bytes_written += fp.write(str(cell).replace('.', ','))
      bytes_written += fp.write('\t')
    bytes_written += fp.write('\n')
  fp.close()

print('\n\t%s bytes escritos >> %s' % (bytes_written, e_filename))