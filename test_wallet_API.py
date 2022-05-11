from datetime import datetime
from threading import Thread
import requests
import time
import json
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class wallet_course(Thread):
    def __init__(self):
        Thread.__init__(self)
        # Данные для работы с таблицей
        self.CREDENTIALS_FILE = 'coursewatcherpy-aff762dfc485.json'
        self.spreadsheetId = "1ti2fLcMBg-rON8BM2i1_6O1GvMJcQoX6uwEcSpZTekk"

    def wallet_info(self):
        timestamp = datetime.now()
        timestamp = timestamp.strftime("%H:%M | %d.%m.%Y")
        response = requests.get("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,RUB")
        data = json.loads(response.text)
        return(timestamp,data)
    
    def add_in_google(self,values_data:list):
            print('[INFO] Работаю с таблицей Google')
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.CREDENTIALS_FILE, [
                                                                        'https://www.googleapis.com/auth/spreadsheets', 
                                                                        'https://www.googleapis.com/auth/drive'
                                                                        ]
                                                                        )
            httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
            service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

            ranges = ["1 list"]
            
            results = service.spreadsheets().values().batchGet(spreadsheetId = self.spreadsheetId, 
                                                ranges = ranges, 
                                                valueRenderOption = 'FORMATTED_VALUE',  
                                                dateTimeRenderOption = 'FORMATTED_STRING').execute() 
            
            try:
                sheet_values = list(results['valueRanges'][0]['values'])
            except KeyError:
                sheet_values = []

            sheet_values.append(values_data)
            results = service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "1 list",
                    "majorDimension": "ROWS",
                    "values": sheet_values
                    }
                ]
            }).execute()
            print('[INFO] Работа с Google таблицей завершена')
        
    def run(self):
        while True:
            data = self.wallet_info()
            data = [data[0],"Bitcoin\BTC",f"{data[1]['RUB']} ₽",f"{data[1]['USD']} $",f"{data[1]['EUR']} €"]
            self.add_in_google(data)
            time.sleep(3600)

if __name__ == "__main__":
    thrd = wallet_course()
    thrd.start()
