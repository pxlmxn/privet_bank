from django.shortcuts import render
import pandas as pd
import requests
from matplotlib import pyplot as plt
import base64
from io import BytesIO
import xmltodict
from datetime import datetime

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

    #График акции
    def get_stock_data():
        ticker = 'YNDX'
        startDate = '2024-03-01'
        finalDate = '2024-04-01'
        interval = '24'
        j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/' + ticker + '/candles.json?from=' + startDate + '&till=' + finalDate + '&interval=' + interval).json()
        data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
        frame = pd.DataFrame(data)
        return frame.drop(columns=['open', 'high', 'low', 'value', 'volume', 'begin'])

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
    def get_courses():
        course = []
        resp = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req=02/04/2024')
        resp_parsed = xmltodict.parse(resp.text)
        valutes = resp_parsed['ValCurs']['Valute']
        for valute in valutes:
            course.append(valute['CharCode'] + ': ' + valute['Value'])
        return course
    

    key_rate = get_key_rate()
    graphic = get_plot_svg(get_stock_data())
    course = get_courses()

    return render(request, 'main.html', context={'key_rate_date': key_rate['@date'], 'key_rate_value': key_rate['@val'], 'graphic': graphic, "course": course})