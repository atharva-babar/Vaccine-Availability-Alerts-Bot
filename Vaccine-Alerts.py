import requests
from datetime import date, timedelta
import json
import telegram
from time import sleep, ctime


def getData(pincode, date):
    try:
        headers = {
            'authority': 'cdn-api.co-vin.in',
            'sec-ch-ua': '^\\^',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'origin': 'https://www.cowin.gov.in',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.cowin.gov.in/',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        params = (
            ('pincode', pincode),
            ('date', date),
        )
        response = requests.get(
            'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin', headers=headers, params=params)
        data = json.loads(response.text)
    except Exception as e:
        data = {"centers": []}
        print(e)
    return data


def formatData(data):
    centersArray = []
    centerData = data['centers']

    for center in centerData:
        centerID = center['center_id']
        centerName = center['name']
        centerPin = center['pincode']
        startTime = center['from']
        endTime = center['to']
        sessions = center['sessions']

        for session in sessions:
            vaccinationDate = session['date']
            minAgeLimit = session['min_age_limit']
            vaccineType = session['vaccine']
            availableCapacity = session['available_capacity']
            feeType = center['fee_type']

            dataDict = {'id': centerID,
                        'center': centerName,
                        'pincode': centerPin,
                        'from': startTime,
                        'to': endTime,
                        'date': vaccinationDate,
                        'ageLimit': minAgeLimit,
                        'vaccineType': vaccineType,
                        'availability': availableCapacity,
                        'feeType': feeType}

            centersArray.append(dataDict)

    return centersArray


def sendAlert(formattedData):
    print(formattedData)
    telegramAlert = f"Age Group: {formattedData['ageLimit']} \nCenter Name: {formattedData['center']} \nPin Code: {formattedData['pincode']} \nDate: {formattedData['date']} \nAvailable Capacity: {formattedData['availability']} \nFee Type: {formattedData['feeType']}  \nVaccine: {formattedData['vaccineType']}"
    telegram.send_msg(telegramAlert)


while True:
    pincode = '440010' # replace your araa pin here.

    today = date.today()
    dateToday = today.strftime("%d-%m-%Y")
    dataToday = getData(pincode, dateToday)

    try:
        dataArrayToday = formatData(dataToday)
        for data in dataArrayToday:
            if data['availability'] >= 1:
                sendAlert(data)
    except Exception as e:
        print(f'Error for DataToday : {e}')

    # Optional for small towns where data is updated on daily basis.
    # Comment out following Try...Except block if not necessary
    dateTomorrow = (today + timedelta(days=1)).strftime("%d-%m-%Y")
    dataTomorrow = getData(pincode, dateTomorrow)
    try:
        dataArrayTomorrow = formatData(dataTomorrow)
        for data in dataArrayTomorrow:
            if data['availability'] >= 1:
                sendAlert(data)
    except Exception as e:
        print(f'Error for DataTomorrow : {e}')

    print(f'Last refresh at time : {ctime()}')

    sleep(5)  # frequency for refreshing data (min = 5 seconds).
