from django.shortcuts import render, redirect
import pandas as pd
import requests
from matplotlib import pyplot as plt
import base64
from io import BytesIO
import xmltodict
import datetime

def main(request):
    #Ключевая ставка
    def get_key_rate():
        url = "http://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n  <soap12:Body>\n    <AllDataInfoXML xmlns=\"http://web.cbr.ru/\" />\n  </soap12:Body>\n</soap12:Envelope>"
        headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8',
        }
        response = requests.post(url, headers=headers, data=payload)
        cbr_daily = xmltodict.parse(response.text)
        return cbr_daily['soap:Envelope']['soap:Body']['AllDataInfoXMLResponse']['AllDataInfoXMLResult']['AllData']['KEY_RATE']

    #Курсы валют
    main_valutes = ['USD', 'EUR', 'GBP', 'CNY', 'JPY', 'BYN']
    def get_courses():
        course = {}
        date = datetime.date.today().strftime('%d/%m/%Y')
        try:
            resp = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}')
            resp_parsed = xmltodict.parse(resp.text)
            valutes = resp_parsed['ValCurs']['Valute']
            for valute in valutes:
                if valute['CharCode'] in main_valutes:
                    course[valute['CharCode']] = valute['Value'][:-2]
        except:
            course = 'Курс валют временно недоступен.'
        return course

    key_rate = get_key_rate()
    course = get_courses()
    
    return render(request, 'main.html', context={'key_rate_date': key_rate['@date'], 'key_rate_value': key_rate['@val'], "course": course.items()})

def valute(request):
    today = datetime.date.today().strftime('%Y-%m-%d')
    return render(request, 'valute.html', context={'today': today})

def stock(request):
    today = datetime.date.today().strftime('%Y-%m-%d')
    #Обработка формы акций
    def get_form_data():
        if request.method == 'GET':
            if request.GET.get('startDate'):
                start_date = request.GET.get('startDate')
                end_date = request.GET.get('endDate')
            else:
                start_date = '2024-01-01'
                end_date = datetime.date.today().strftime('%Y-%m-%d')
            if request.GET.get('ticker'):
                ticker = request.GET.get('ticker')
            else:
                ticker = 'YNDX'
            if request.GET.get('interval'):
                interval = request.GET.get('interval')
            else:
                interval = '24'
            return(start_date, end_date, interval, ticker)
        
    #Сборка данных об акциях
    def get_stock_data(startDate, finalDate, interval, ticker):
        try:
            j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/' + ticker + '/candles.json?from=' + startDate + '&till=' + finalDate + '&interval=' + interval).json()
            data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
            stock_data = pd.DataFrame(data)
            stock_data = stock_data.drop(columns=['open', 'high', 'low', 'value', 'volume', 'begin'])
            dates = {}
            dates['end'] = []
            for date in stock_data['end']:
                dates['end'].append(date[:10])
            stock_data['end'] = dates['end']
        except:
            stock_data = None
        stock_dates = stock_data['end'].tolist()
        stock_prices = stock_data['close'].tolist()
        return stock_dates, stock_prices
    
    startDate, finalDate, interval, ticker = get_form_data()

    stock_dates, stock_prices = get_stock_data(startDate, finalDate, interval, ticker)

    return render(request, 'stock.html', context={'stock_dates': stock_dates, 'stock_prices': stock_prices, 'today': today})