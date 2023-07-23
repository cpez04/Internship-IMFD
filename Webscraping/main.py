import requests
import pandas as pd 
import time 

url = "http://siedt.spd.gov.cl/"
user = "estacionspd1"
psw = "7XB9jWr8"

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
    'Zm0gg3rNB6OzD4uO74M7Dk1htZoFniULoaxlvcs': '0a831e308bb3af309f55b0bde5921f11',
    'ci_session': 'k2jh881oi7ohcdstkeob5b8ederkjqgs',
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


#Given providence id, prints out comunas and corresponding ID - funciona bien
provincia_id = '136'
data = 'field=Comuna&value_default=(Todas)&parent_id=' + provincia_id
response_comunas = requests.post('https://siedt.spd.gov.cl/index.php/app/get_values_list/', cookies=cookies, headers=headers, data=data)
comunas = parse_options(response_comunas.text)
print(comunas)

barrio_id = '13'
data = 'field=Barrio&value_default=(Todos)&parent_id=' + barrio_id
response_barrios = requests.post('https://siedt.spd.gov.cl/index.php/app/get_values_list/', cookies=cookies, headers=headers, data=data)
answer = parse_options(response_barrios.text)
print(answer)






#GET polígono de un feature - no funciona 
data = 'metodo=filter&forma=filter&poligono=&region=13&provincia=131&categoria=-1&delito^%^5B^%^5D=-1&anio=2013&mes=-1'
response = requests.post('https://siedt.spd.gov.cl/index.php/app/find_points', cookies=cookies, headers=headers, data=data)
print(response.text)
