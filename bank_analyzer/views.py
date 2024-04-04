from django.shortcuts import render, redirect
import pandas as pd
import requests
import xmltodict
import datetime

def main(request):
    #Ключевая ставка
    def get_key_rate():
        start_date = '2024-01-01'
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        url = "http://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
        data = f'''<?xml version=\"1.0\" encoding=\"utf-8\"?>\n
            <soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n
            <soap12:Body>\n
                <KeyRate xmlns=\"http://web.cbr.ru/\">\n 
                    <fromDate>{start_date}</fromDate>\n      
                    <ToDate>{end_date}</ToDate>\n    
                </KeyRate>\n
            </soap12:Body>\n
            </soap12:Envelope>'''
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        response = requests.request("POST", url, headers=headers, data=data)
        resp_dict= xmltodict.parse(response.text)
        key_rate = resp_dict['soap:Envelope']['soap:Body']['KeyRateResponse']['KeyRateResult']['diffgr:diffgram']['KeyRate']['KR']
        key_dates = []
        key_rates =[]
        for i in key_rate:
            key_dates.append(i['DT'][:10])
            key_rates.append(i['Rate'])
        return key_dates, key_rates

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
    
    #График акций
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

    course = get_courses()
    key_dates, key_rates = get_key_rate() 
    stock_dates, stock_prices = get_stock_data("2024-01-01", datetime.date.today().strftime('%Y-%m-%d'), "24", "YNDX")
    
    return render(request, 'main.html', context={"course": course.items(), 'key_dates': key_dates, 'key_rates': key_rates, 'stock_dates': stock_dates, 'stock_prices': stock_prices})

def valute(request):
    today = datetime.date.today().strftime('%d/%m/%Y')
    
    #if request.method == 'GET':
    #    start_date = request.GET.get('startDate')
    #    end_date = request.GET.get('endDate')
    #else:
    start_date = '01/01/2023'
    end_date = datetime.datetime.now().strftime('%d/%m/%Y')

    url = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start_date}&date_req2={end_date}&VAL_NM_RQ=R01235"
    response = requests.request("POST", url,)
    resp_dict = xmltodict.parse(response.text)
    records = resp_dict['ValCurs']['Record']
    dates = []
    rates = []
    for m in records:
        dates.append(m['@Date'])
        rates.append(float(m['VunitRate'].replace(',', '.')))
    return render(request, 'valute.html', context={'today': today, 'dates': dates, 'rates': rates})

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

def loan(request):
    return render(request, 'loan.html')