from django.shortcuts import render
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

    #Обработка формы акций
    def get_form_data():
        if request.method == 'GET':
            if request.GET.get('startDate'):
                start_date = request.GET.get('startDate')
                end_date = request.GET.get('endDate')
            else:
                start_date = '2024-01-01'
                end_date = datetime.date.today().strftime('%Y-%m-%d')
            stock_dates = [start_date, end_date]
            return stock_dates
    #Сборка данных об акциях
    def get_stock_data(stock_dates):
        ticker = 'YNDX'
        startDate = stock_dates[0]
        finalDate = stock_dates[1]
        interval = '24'
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
            j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/' + ticker + '/candles.json?from=' + startDate + '&till=' + finalDate + '&interval=' + interval).json()
            data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
            stock_data = pd.DataFrame(data)
            stock_data = stock_data.drop(columns=['open', 'high', 'low', 'value', 'volume', 'begin'])
            dates = {}
            dates['end'] = []
            for date in stock_data['end']:
                dates['end'].append(date[:10])
            stock_data['end'] = dates['end']
        return stock_data

    #График акции
    def get_graph_svg():
        buffer = BytesIO()
        plt.savefig(buffer, format='svg')
        buffer.seek(0)
        image_svg = buffer.getvalue()
        graph = base64.b64encode(image_svg)
        graph = graph.decode('utf-8')
        buffer.close()
        return graph
    
    def get_plot_svg(frame):
        plt.switch_backend('SVG')
        plt.figure(figsize=(15, 6))
        plt.plot(list(frame['end']), list(frame['close']))
        plt.xlabel('Дата')
        plt.ylabel('Стоимость, руб')
        plt.xticks(rotation=70)
        graph = get_graph_svg()
        return graph

    #Курсы валют
    main_valutes = ['USD', 'EUR', 'GBP', 'CNY', 'JPY', 'BYN']
    def get_courses():
        course = []
        try:
            resp = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req=02/04/2024')
            resp_parsed = xmltodict.parse(resp.text)
            valutes = resp_parsed['ValCurs']['Valute']
            for valute in valutes:
                if valute['CharCode'] in main_valutes:
                    course.append(valute['CharCode'] + ': ' + valute['Value'][:-2])
        except:
            course = 'Курс валют временно недоступен.'
        return course

    key_rate = get_key_rate()
    graphic = get_plot_svg(get_stock_data(get_form_data()))
    course = get_courses()
    return render(request, 'main.html', context={'key_rate_date': key_rate['@date'], 'key_rate_value': key_rate['@val'], 'graphic': graphic, "course": course})