import time
import sqlite3 as sql


field_spec = [
    {'name': 'fecha', 'type': 'd'},
    {'name': 'sucursal', 'type': 's'},
    {'name': 'tarjeta', 'type': 's'},
    {'name': 'lote', 'type': 'i'},
    {'name': 'importe', 'type': 'f'}
]

db = sql.connect('data.db')


def parseLine(line, sep=',', old='', new=''):
    fields = line.split(sep)

    i = 0
    n = len(fields)

    if n == len(field_spec):
        while (i < n):
            fields[i] = fields[i].replace(old, new)

            field_type = field_spec[i]['type']

            if field_type == 'd':
                fields[i] = float(time.mktime(time.strptime(fields[i],
                                                            '%d/%m/%Y'))) - time.timezone
            elif field_type == 'i':
                fields[i] = int(fields[i])
            elif field_type == 'f':
                fields[i] = float(fields[i])
            elif field_type == 's':
                fields[i] = fields[i].lower()
            i += 1

    return tuple(fields)


def saveToDb(field_arr):
    sql_st = 'INSERT INTO cupones ('
    field_names = ''
    value_blanks = ''

    i = 0
    n = len(field_spec)
    while (i < n):
        field_names += field_spec[i]['name'] + ','
        value_blanks += '?,'
        i += 1

    # Remove last ','
    field_names = field_names[:len(field_names) - 1]
    value_blanks = value_blanks[:len(value_blanks) - 1]

    sql_st += field_names + ') VALUES (' + value_blanks + ')'

    db.executemany(sql_st, field_arr)
    db.commit()


fp = open('Cupones.csv', 'rt')
# Skip headers
fp.readline()

field_arr = []
for line in fp:
    field_arr.append(parseLine(line, ';', ',', '.'))

saveToDb(field_arr)
db.close()
