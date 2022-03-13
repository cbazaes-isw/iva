import requests
import json
import uuid


authentication_url      = "https://zeusr.sii.cl/cgi_AUT2000/CAutInicio.cgi"
query_resume_url        = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen"
query_purchase_details  = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getDetalleCompra"
query_sales_details     = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getDetalleVenta"


def get_session_cookies(user_rut, password):

    dv = user_rut.split("-")[1]
    user_rut = user_rut.split("-")[0]

    payload = f'rut={user_rut}&dv={dv}&referencia=https%253A%252F%252Fwww4.sii.cl%252Fconsdcvinternetui%252F&clave={password}'
    headers = {
        'Cookie': 's_cc=true; s_sq=%5B%5BB%5D%5D; dtCookie=22$04AF043D811DF3E7C4E0105EF9D7B06C|ea7c4b59f27d43eb|0|b23bdcbbe9c1ae0d|0;'
    }

    response = requests.request(
        "POST", authentication_url, headers=headers, data=payload)

    if (response.status_code != 200):
        return dict()

    d = dict()
    for c in response.cookies:
        d[c.name] = c

    return d


def get_resume(cookies, company_rut, query_year, query_month, is_sale):

    dv = company_rut.split("-")[1]
    company_rut = company_rut.split("-")[0]

    payload = json.dumps({
        "metaData": {
            "namespace": "cl.sii.sdi.lob.diii.consdcv.data.api.interfaces.FacadeService/getResumen",
            "conversationId": cookies["CSESSIONID"].value,
            "transactionId": str(uuid.uuid4()),
            "page": None
        },
        "data": {
            "rutEmisor": str(company_rut),
            "dvEmisor": str(dv),
            "ptributario": f'{query_year}{query_month:02d}',
            "estadoContab": "REGISTRO",
            "operacion": "VENTA" if is_sale else "COMPRA",
            "busquedaInicial": True
        }
    })

    headers = {
        'Cookie': get_cookie_string(cookies),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", query_resume_url, headers=headers, data=payload)

    resume = json.loads(response.content)
    if resume['respEstado']['codRespuesta'] != 0:
        return dict()

    d = dict()
    for r in resume["data"]:
        d[str(r['rsmnTipoDocInteger'])] = r

    return d


def get_purchases(cookies, company_rut, query_year, query_month):

    resume = get_resume(
        cookies, company_rut, query_year, query_month, False)

    dv = company_rut.split("-")[1]
    company_rut = company_rut.split("-")[0]

    headers = {
        'Cookie': get_cookie_string(cookies),
        'Content-Type': 'application/json'
    }

    details = dict()

    for k, v in resume.items():

        payload = json.dumps({
            "metaData": {
                "namespace": "cl.sii.sdi.lob.diii.consdcv.data.api.interfaces.FacadeService/getDetalleCompra",
                "conversationId": cookies["CSESSIONID"].value,
                "transactionId": str(uuid.uuid4()),
                "page": None
            },
            "data": {
                "rutEmisor": str(company_rut),
                "dvEmisor": str(dv),
                "ptributario": f'{query_year}{query_month:02d}',
                "codTipoDoc": k,
                "operacion": "COMPRA",
                "estadoContab": "REGISTRO"
            }
        })

        response = requests.request(
            "POST", query_purchase_details, headers=headers, data=payload)

        detail = json.loads(response.content)
        if detail['respEstado']['codRespuesta'] != 0:
            return dict()

        for d in detail["data"]:
            key = f'{d["detRutDoc"]}-{d["detDvDoc"]}_{k}_{d["detNroDoc"]}'
            d['detTipoDoc'] = int(k) # Agrega el tipo de documento al diccionario, por que no viene.
            details[key] = d

    return details


def get_sales(cookies, company_rut, query_year, query_month):

    resume = get_resume(
        cookies, company_rut, query_year, query_month, True)

    dv = company_rut.split("-")[1]
    company_rut = company_rut.split("-")[0]

    headers = {
        'Cookie': get_cookie_string(cookies),
        'Content-Type': 'application/json'
    }

    details = dict()

    for k, v in resume.items():

        payload = json.dumps({
            "metaData": {
                "namespace": "cl.sii.sdi.lob.diii.consdcv.data.api.interfaces.FacadeService/getDetalleVenta",
                "conversationId": cookies["CSESSIONID"].value,
                "transactionId": str(uuid.uuid4()),
                "page": None
            },
            "data": {
                "rutEmisor": str(company_rut),
                "dvEmisor": str(dv),
                "ptributario": f'{query_year}{query_month:02d}',
                "codTipoDoc": k,
                "operacion": "",
                "estadoContab": ""
            }
        })

        response = requests.request(
            "POST", query_sales_details, headers=headers, data=payload)

        detail = json.loads(response.content)
        if detail['respEstado']['codRespuesta'] != 0:
            return dict()

        for d in detail["data"]:
            key = f'{company_rut}-{dv}_{k}_{d["detNroDoc"]}'
            details[key] = d

    return details


def get_cookie_string(cookies):
    s = '; '.join([f'{k}={v.value}' for k, v in cookies.items()])
    return s
