from functools import reduce
import utils.sii as siiUtils


user_rut = '15026353-0'
password = 'esanchez18'

cookies = siiUtils.get_session_cookies(user_rut, password)

company_rut = '77193447-1'
query_year = 2022
query_month = 2


sales = siiUtils.get_sales(cookies, company_rut, query_year, query_month)
purchases = siiUtils.get_purchases(cookies, company_rut, query_year, query_month)


sales_total = reduce((lambda x, y: x + y), [int(v['detMntIVA']) for k, v in sales.items()])
purchases_total = reduce((lambda x, y: x + y), [int(v['detMntIVA']) for k, v in purchases.items()])
diff = sales_total - purchases_total


print(f'TOTAL IVA VENTAS: {sales_total}')
print(f'TOTAL IVA COMPRAS: {purchases_total}')
print(f'IVA A PAGAR: {diff}')
