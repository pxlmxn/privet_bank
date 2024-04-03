from django.shortcuts import render
import pandas as pd
import requests
from matplotlib import pyplot as plt
import base64
from io import BytesIO
import xmltodict
from datetime import datetime

def main(request):
    ticker = 'YNDX'
    startDate = '2024-03-01'
    finalDate = '2024-04-01'
    interval = '24'
    j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/' + ticker + '/candles.json?from=' + startDate + '&till=' + finalDate + '&interval=' + interval).json()
    data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
    frame = pd.DataFrame(data)
    dates = []
    print(list(frame['end']))

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
    
    graphic = get_plot_svg(frame)

    course = []
    resp = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req=02/04/2024')
    resp_parsed = xmltodict.parse(resp.text)
    valutes = resp_parsed['ValCurs']['Valute']
    for valute in valutes:
        course.append(valute['CharCode'] + ': ' + valute['Value'])

    return render(request, 'main.html', context={'ticker': ticker, 'graphic': graphic, "course": course})