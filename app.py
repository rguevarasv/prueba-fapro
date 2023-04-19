import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, Response


class UfService:
    def __init__(self):
        self.base_url = "https://www.sii.cl/valores_y_fechas/uf/"

    def obtener_uf_por_fecha(self, mes=None, anio=None):
        print(mes)
        print(anio)
        url = f"{self.base_url}uf{anio}.htm"
        # url = "https://www.sii.cl/valores_y_fechas/uf/uf2022.htm"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            rows = soup.find('div', attrs={"id": f"mes_{mes}"}).find('table').find('tbody').find_all('tr')
        except AttributeError:
            rows = None

        datos = []
        if rows is not None:
            for fila in rows[1:]:
                celdas = fila.find_all("td")
                fila_datos = []
                for celda in celdas:
                    fila_datos.append(celda.text)
                datos.append(fila_datos)

            # Buscamos la longitud máxima de cualquier fila en la tabla
            max_longitud = max(len(fila) for fila in datos)

            # Añadimos elementos faltantes a las filas más cortas con un valor por defecto
            for fila in datos:
                while len(fila) < max_longitud:
                    fila.append(None)

            # Transponemos los datos de la tabla para obtener las columnas en lugar de las filas
            columnas = list(map(list, zip(*datos)))

            # Unimos todos los datos en una sola lista, quitando los valores vacíos
            resultado = [valor for columna in columnas for valor in columna if valor not in (None, "")]
        else:
            resultado = ["0"]


        return resultado

    def obtener_elemento(self, dia=None, mes=None, anio=None):
        meses = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}

        try:
            resultado = self.obtener_uf_por_fecha(meses[mes], anio)

            if len(resultado) > dia:
                resultado = resultado[dia]
            else:
                resultado = "No hay datos que consultar"
        except IndexError:
            raise ValueError('Error al obtener indice')
        except KeyError:
            raise ValueError('Error al obtener key')

        return resultado


app = Flask(__name__)
uf_service = UfService()


@app.route('/uf', methods=['GET'])
def obtener_uf():
    if not request.is_json:
        return jsonify({"msg": "Es necesario enviar datos JSON"}), 400

    params = request.get_json()
    dia = params.get('dia', None)
    mes = params.get('mes', None)
    anio = params.get('anio', None)

    if not dia or dia == "":
        return jsonify({"msg": "Es necesario parametro dia"}), 400
    if not mes:
        return jsonify({"msg": "Es necesario parametro mes"}), 400
    if not anio:
        return jsonify({"msg": "Es necesario parametro anio"}), 400

    valores_uf = uf_service.obtener_elemento(dia, mes, anio)

    try:
        if valores_uf != "" or valores_uf != 0:
            return jsonify({"valor": valores_uf}), 200
    except ValueError as error:
        mensaje = str(error)
        return Response(mensaje, status=400)


if __name__ == '__main__':
    app.run()
