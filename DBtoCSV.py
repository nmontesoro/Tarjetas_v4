import csv
import sqlite3 as sql
from datetime import datetime


class cupones():
    db = None

    def __init__(self):
        self.db = sql.connect('data.db')

    def _CursorToCSV(self, cur, sep=',', old='', new=''):
        csv_content = ''

        for row in cur:
            for cell in row:
                csv_content += str(cell).replace(old, new) + sep
            csv_content += '\n'

        return csv_content
    
    def _GetColumnNames(self, tablename):
        cur = self.db.execute('PRAGMA TABLE_INFO(%s)' % (tablename))
        colnames = []
        for row in cur:
            colnames.append(row[1])
        return colnames

    def _ParseCSV(self, cur, tablename=''):
        fecha = 'Generado el ' + datetime.now().strftime(r'%Y-%m-%d')
        csv_content = fecha + '\n'

        if not tablename == '':
            colnames = self._GetColumnNames(tablename)
            for col in colnames:
                csv_content += col + ';'
            csv_content += '\n'

        csv_content += self._CursorToCSV(cur, sep=';', old='.', new=',')
        return csv_content

    def GetCuponesPagados(self):
        sql_pagados = '''SELECT * FROM export
                         WHERE liquidado IS NOT NULL
                         AND ABS(diferencia) < 0.5'''

        cur = self.db.execute(sql_pagados).fetchall()

        return self._ParseCSV(cur, 'export')

    def GetCuponesNoPagados(self):
        sql_no_pagados = '''SELECT * FROM export
                            WHERE liquidado IS NULL'''

        cur = self.db.execute(sql_no_pagados).fetchall()

        return self._ParseCSV(cur, 'export')

    def GetCuponesProblematicos(self):
        # Cupones pagados parcialmente, o errores de carga

        sql_problematicos = '''SELECT * FROM export
                               WHERE liquidado IS NOT NULL
                               AND ABS(diferencia) >= 0.5'''

        cur = self.db.execute(sql_problematicos).fetchall()

        return self._ParseCSV(cur, 'export')

    def ExportCupones(self):
        steps = {
            'pagados.csv': self.GetCuponesPagados(),
            'nopagados.csv': self.GetCuponesNoPagados(),
            'problematicos.csv': self.GetCuponesProblematicos()
        }

        for filename, content in steps.items():
            fp = open(filename, 'wt')
            fp.write(content)
            fp.close()


if __name__ == '__main__':
    c = cupones()
    c.ExportCupones()
