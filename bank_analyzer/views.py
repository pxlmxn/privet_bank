from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
import pandas as pd
import requests
import xmltodict
import datetime
from .models import Transaction

def main(request):
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    #Ключевая ставка
    def get_key_rate():
        key_start_date = '2023-01-01'
        key_end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if request.method == 'POST' and not request.POST.get('start_date', '') == request.POST.get('end_date', ''):
            key_start_date = request.POST.get('start_date', '')
            key_end_date = request.POST.get('end_date', '')

        url = "http://cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
        data = f'''<?xml version=\"1.0\" encoding=\"utf-8\"?>\n
            <soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n
            <soap12:Body>\n
                <KeyRate xmlns=\"http://web.cbr.ru/\">\n 
                    <fromDate>{key_start_date}</fromDate>\n      
                    <ToDate>{key_end_date}</ToDate>\n    
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
        return reversed(key_dates), reversed(key_rates)

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
            j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/YNDX/candles.json?from=2024-01-01&till=' + datetime.date.today().strftime('%Y-%m-%d') + '&interval=24').json()
            data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
            stock_data = pd.DataFrame(data)
            stock_data = stock_data.drop(columns=['open', 'high', 'low', 'value', 'volume', 'begin'])
            dates = {}
            dates['end'] = []
            for date in stock_data['end']:
                dates['end'].append(date[:10])
            stock_data['end'] = dates['end']
        stock_dates = stock_data['end'].tolist()
        stock_prices = stock_data['close'].tolist()
        return stock_dates, stock_prices

    course = get_courses()
    key_dates, key_rates = get_key_rate() 
    stock_dates, stock_prices = get_stock_data("2024-01-01", datetime.date.today().strftime('%Y-%m-%d'), "24", "YNDX")
    
    return render(request, 'main.html', context={"course": course.items(), 'key_dates': key_dates, 'key_rates': key_rates, 'stock_dates': stock_dates, 'stock_prices': stock_prices, 'today': today})

def valute(request):
    today = datetime.date.today().strftime('%Y-%m-%d')

    all_valutes = {'R01010': 'Австралийский доллар', 'R01020A': 'Азербайджанский манат', 'R01035': 'Фунт стерлингов Соединенного королевства', 'R01060': 'Армянских драмов', 'R01090B': 'Белорусский рубль', 'R01100': 'Болгарский лев', 'R01115': 'Бразильский реал', 'R01135': 'Венгерских форинтов', 'R01150': 'Вьетнамских донгов', 'R01200': 'Гонконгский доллар', 'R01210': 'Грузинский лари', 'R01215': 'Датская крона', 'R01230': 'Дирхам ОАЭ', 'R01235': 'Доллар США', 'R01239': 'Евро', 'R01240': 'Египетских фунтов', 'R01270': 'Индийских рупий', 'R01280': 'Индонезийских рупий', 'R01335': 'Казахстанских тенге', 'R01350': 'Канадский доллар', 'R01355': 'Катарский риал', 'R01370': 'Киргизских сомов', 'R01375': 'Китайский юань', 'R01500': 'Молдавских леев', 'R01530': 'Новозеландский доллар', 'R01535': 'Норвежских крон', 'R01565': 'Польский злотый', 'R01585F': 'Румынский лей', 'R01589': 'СДР (специальные права заимствования)', 'R01625': 'Сингапурский доллар', 'R01670': 'Таджикских сомони', 'R01675': 'Таиландских батов', 'R01700J': 'Турецких лир', 'R01710A': 'Новый туркменский манат', 'R01717': 'Узбекских сумов', 'R01720': 'Украинских гривен', 'R01760': 'Чешских крон', 'R01770': 'Шведских крон', 'R01775': 'Швейцарский франк', 'R01805F': 'Сербских динаров', 'R01810': 'Южноафриканских рэндов', 'R01815': 'Вон Республики Корея', 'R01820': 'Японских иен'}
    
    if request.method == 'POST':
        if not request.POST.get('startDate') == request.POST.get('endDate'):
            start_date = request.POST.get('startDate')
            start_date = start_date[8:] + '/' + start_date[5:7] + '/' + start_date[:4]
            end_date = request.POST.get('endDate')
            end_date = end_date[8:] + '/' + end_date[5:7] + '/' + end_date[:4]
        else:
            start_date = '01/01/2024'
            end_date = datetime.datetime.now().strftime('%d/%m/%Y')
        if request.POST.get('id'):
            id = request.POST.get('id')
        else:
            id = "R01235"

    try:
        url = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start_date}&date_req2={end_date}&VAL_NM_RQ={id}"
        response = requests.request("POST", url,)
        resp_dict = xmltodict.parse(response.text)
        records = resp_dict['ValCurs']['Record']
    except:
        url = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2024&date_req2={datetime.datetime.now().strftime('%d/%m/%Y')}&VAL_NM_RQ=R01235"
        response = requests.request("POST", url,)
        resp_dict = xmltodict.parse(response.text)
        records = resp_dict['ValCurs']['Record']
    dates = []
    rates = []
    for i in records:
        dates.append(i['@Date'])
        rates.append(float(i['VunitRate'].replace(',', '.')))
    return render(request, 'valute.html', context={'today': today, 'dates': dates, 'rates': rates, 'all_valutes': all_valutes.items()})

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
        
    #Сбор данных об акциях
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

class CardOperation(View):
    def get(self, request):
        transactions = {}
        all_transactions = Transaction.objects.all()
        for transaction in all_transactions:
            transactions[transaction.shop] = transaction.amount
        return JsonResponse({"status": 200, "transactions": transactions})
    
    def post(self, request):
        card_id = int(request.POST.get('card_id'))
        amount = int(request.POST.get('amount'))
        shop = request.POST.get('shop')
        Transaction.objects.create(
            card_id = card_id,
            amount = amount,
            shop = shop
        )
        return JsonResponse({"status": 200})

    def patch(self, request):
        return JsonResponse({"status": 200, "message": "patch запрос"})

    def delete(self, request):
        return JsonResponse({"status": 200, "message": "delete запрос"})