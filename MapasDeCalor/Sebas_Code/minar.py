import requests
import pandas as pd
import numpy as np
from time import sleep
import pickle

url = "https://siedt.spd.gov.cl/"
user = "estacionspd5"
psw = "3tmMWeC3"

def parse_options(options):
    """
    Parsea un objeto options de html en forma string a un diccionario.
    """
    options = options.split("</option>")
    options = [option.split(">") for option in options]
    options = [(option[1], option[0].split("value=")[1]) for option in options if len(option) == 2]
    options = {option[0]: option[1] for option in options}
    return options


# INICIAR SESIÓN MANUALMENTE Y COPIAR LOS VALORES DE ESTAS COOKIES
cookies = {
    'Zm0gg3rNB6OzD4uO74M7Dk1htZoFniULoaxlvcs': 'd9576596f2f751d964656d2eb9a24b0e',
    'ci_session': 'ehqj4fkauq2ap41dt4urcnj5o1g065kr',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://siedt.spd.gov.cl',
    'Connection': 'keep-alive',
    'Referer': 'https://siedt.spd.gov.cl/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


with open('barrios_por_comuna_v2.pickle', 'rb') as handle:
    barrios_por_comuna = pickle.load(handle)


for comuna in barrios_por_comuna:
  id_comuna =  barrios_por_comuna[comuna][0]
  barrios = barrios_por_comuna[comuna][1]
  for barrio in barrios:
    id_barrio = barrios[barrio][0]
    for año in range(2013,2023):
        try:
          data = f'metodo=filter&forma=filter&poligono=&region=13&provincia=131&comuna={id_comuna}&barrio={id_barrio}&categoria=-1&delito^%^5B^%^5D=-1&anio={año}&mes=-1'
          print("Query:", data)
          response = requests.post('https://siedt.spd.gov.cl/index.php/app/find_points', cookies=cookies, headers=headers, data=data)
          if response.status_code != 200:
            raise Exception("Status code != 200")
          df = pd.DataFrame(response.json()['CP_data'])
          df['Comuna'] = comuna
          df['ID_Comuna'] = id_comuna
          df['Barrio'] = barrio
          df['ID_Barrio'] = id_barrio
          nombre = comuna + "_" + barrio + "_" + str(año)
          # replace all windows forbidden characters in name
          nombre = nombre.replace('/', '').replace('\\', '').replace(':', '').replace('"', '').replace('*', '')
          df.to_csv(f'delitos/{nombre}.csv')
          # Conteo
          r += 1
          print(comuna, barrio, año, round(r/30420*100, 2))
        except Exception as e:
          # Si se cae a la request, el comuna,barrio,año no se agrega a completados.
          # Tambien guardamos el estado de completados, pero de igual forma puede obtenerse
          # corriendo recuento.py
          print(e)
