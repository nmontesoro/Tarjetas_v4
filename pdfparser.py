"""
pdfparser: Toma un archivo pdf y lo procesa en busca de liquidaciones de
tarjetas de débito
"""


import re as regex
import datetime as dt
import PyPDF2

# regex plata: [\d\.]*,\d{2}
# Liq\. N. (\d{8}) - Lote N. [\n]?\d{4}\s*(\d{1,}) Ventas? Tj. ?D.bito\$([\d\. ]*,\d{2})
# \d{1,} Ventas? (?:(?:en\s*\d{1,} pagos?)|(?:Tj. ?D.bito))\$[\d\. ]*,\d{2})


class PdfParser():
    file_obj = None
    pdf_obj = None
    tarjeta = ''
    sucursal = ''

    prototype = {
        'fpago': 0.0,
        'liqno': 0,
        'lote': 0,
        'arancel': 0.0,
        'impuestos': 0.0,
        'importe': 0.0,
        'adicionales': 0.0
    }

    def __init__(self, filename):
        self.file_obj = open(filename, 'rb')
        self.pdf_obj = PyPDF2.PdfFileReader(self.file_obj)
        self._get_datos_liquidacion(filename)

    def _get_datos_liquidacion(self, filename):
        filename = filename.lower()
        datos = regex.findall(r'\d{4}-\d{2}-(\w+)-([\w ]*)\.pdf', filename)
        self.tarjeta = datos[0][0]
        self.sucursal = datos[0][1]

    def _extract_text(self):
        raw_text = ''
        n = self.pdf_obj.numPages
        i = 0
        while (i < n):
            raw_text += self.pdf_obj.getPage(i).extractText()
            i += 1
        return raw_text

    def _parse_visa(self):
        liqs = []

        raw_text = self._extract_text()

        filas = regex.findall(
            r'FECHA DE PAGO[\s\S]*?Total del d.a (?:\$[\d\. ]*,\d{2}){3}',
            raw_text)
        ano = int(regex.findall(r'\d{2}/\d{2}/(\d{4})\d{15}', raw_text)[0])

        # OJO: Matchea credito y debito!
        # Devuelve lista de listas
        # re_lotes = regex.compile(r'Liq\. N. (\d{8}).*?Lote N. (\d{4}).*?'
        #          + r'\d{1,} Ventas? (?:(?:en\s*\d{1,} pagos?.*?)|'
        #          + r'(?:Tj. ?D.bito))\$([\d\. ]*,\d{2})')
        re_liqnos = regex.compile(r'Liq\. N. (\d{8})')
        re_lotes = regex.compile(r'Lote N. (\d{4})')
        re_importes = regex.compile(
            r'\d{1,} Ventas? (?:(?:en\s*\d{1,} pagos?.*?)|(?:Tj. ?D.bito))'
            + r'\$([\d\. ]*,\d{2})')
        re_arancel = regex.compile(r'Arancel\$([\d\. ]*,\d{2})')
        re_impuestos = regex.compile(r'Impositivas\$([\d\. ]*,\d{2})')
        re_lapos = regex.compile(r'LaPos\$([\d\. ]*,\d{2})')
        re_financieros = regex.compile(r'Financieros\$([\d\. ]*,\d{2})')
        re_adicionales = regex.compile(r'Adicional\$([\d\. ]*,\d{2})')
        re_fpago = regex.compile(r'FECHA DE PAGO\s*?(\d{2}/\d{2})')

        for fila in filas:
            fpago = dt.datetime.strptime(re_fpago.findall(
                fila)[0] + '/' + str(ano), '%d/%m/%Y').timestamp()

            try:
                arancel = self._money_to_float(
                    re_arancel.findall(fila)[0])
            except:
                arancel = 0.0

            try:
                impuestos = self._money_to_float(
                    re_impuestos.findall(fila)[0])
            except:
                impuestos = 0.0

            try:
                lapos = self._money_to_float(re_lapos.findall(fila)[0])
            except:
                lapos = 0.0

            try:
                financieros = self._money_to_float(
                    re_financieros.findall(fila)[0])
            except:
                financieros = 0.0

            try:
                adicionales = self._money_to_float(
                    re_adicionales.findall(fila)[0])
            except:
                adicionales = 0.0

            lotes = re_lotes.findall(fila)
            liqnos = re_liqnos.findall(fila)
            importes = re_importes.findall(fila)
            n = len(lotes)
            i = 0
            while (i < n):
                self.prototype['fpago'] = fpago
                self.prototype['liqno'] = int(liqnos[i])
                self.prototype['lote'] = int(lotes[i])
                self.prototype['importe'] = self._money_to_float(importes[i])
                self.prototype['arancel'] = arancel / n
                self.prototype['impuestos'] = impuestos / n
                self.prototype['adicionales'] = (
                    lapos + financieros + adicionales) / n
                liqs.append(self.prototype.copy())
                i += 1

        return liqs

    def _money_to_float(self, money):
        return float(money.replace('.', '').replace(',', '.'))

    def _parse_maestro(self):
        liqs = []

        raw_text = self._extract_text()

        filas = regex.findall(
            r'Venta ctdo.*?F. Pres\d{2}/\d{2}/\d{4}', raw_text)

        # Matchea lote e importe
        re_ops = regex.compile(
            r'Venta ctdo\d{2}/\d{2}/\d{2}\d{6}(\d{3})\d{8}([\d\.]*,\d{2})')
        re_arancel = regex.compile(r'ARANCEL-\$([\d\.]*,\d{2})')
        re_iva = regex.compile(r'21,00\%-\$([\d\.]*,\d{2})')
        # OJO! Puede matchear mas de una retencion!!
        re_retenciones = regex.compile(r'RETENCION.*?-\$([\d\.]*,\d{2})')
        # OJO! Matchea op. intl. e iva !
        re_ops_intl = regex.compile(r'OPER\. INT.*?-\$([\d\.]*,\d{2})')
        re_liqno = regex.compile(r'(\d{6})\d{2}/\d{2}/\d{4}')
        # La regex esta bien. Hecha asi por el formato de raw_text
        re_fpago = regex.compile(r'F\. Pres(\d{2}/\d{2}/\d{4})')
        re_percepciones = regex.compile(r'PER.*?-\$([\d\.]*,\d{2})')
        for fila in filas:
            fpago = dt.datetime.strptime(re_fpago.findall(fila)[
                                         0], '%d/%m/%Y').timestamp()

            try:
                arancel = self._money_to_float(
                    re_arancel.findall(fila)[0])
            except:
                arancel = 0.0

            try:
                impuestos = self._money_to_float(re_iva.findall(fila)[0])
            except:
                impuestos = 0.0

            try:
                liqno = int(re_liqno.findall(fila)[0])
            except:
                liqno = 0

            op_intl = 0.0
            for intlop in re_ops_intl.findall(fila):
                op_intl += self._money_to_float(intlop)

            retenciones = 0.0
            for ret in re_retenciones.findall(fila):
                retenciones += self._money_to_float(ret)

            for per in re_percepciones.findall(fila):
                impuestos += self._money_to_float(per)

            ops = re_ops.findall(fila)
            n = len(ops)
            i = 0
            while (i < n):
                self.prototype['fpago'] = fpago
                self.prototype['liqno'] = liqno
                self.prototype['lote'] = int(ops[i][0])
                self.prototype['importe'] = self._money_to_float(ops[i][1])
                self.prototype['arancel'] = arancel / n
                self.prototype['impuestos'] = (impuestos + retenciones) / n
                self.prototype['adicionales'] = (op_intl) / n
                liqs.append(self.prototype.copy())
                i += 1

        return liqs

    # def _parseMastercard(self):
    #   liqs = []

    #   raw_text = self._extractText()

    #   filas = regex.findall(r'lote ctdo.*?F\. Pres\d{2}/\d{2}/\d{4}', raw_text)

    #   for fila in filas:

    def get_liquidaciones(self):
        liqs = []

        if (self.tarjeta == 'visa' or self.tarjeta == 'cabal'):
            liqs = self._parse_visa()
        elif (self.tarjeta == 'maestro'):
            liqs = self._parse_maestro()
        else:
            print('No implementado...')

        return liqs


if __name__ == '__main__':
    p = PdfParser('2018-10-maestro-libertad.pdf')
    liqs = p.get_liquidaciones()

    for liq in liqs:
        for key, value in liq.items():
            print(key + ': ' + str(value))
        print('\n')
