# -*- coding: UTF-8 -*-
import datetime
import time
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


class Avito_Watcher(Thread):
    def __init__(self):
        # Инициализация потока
        Thread.__init__(self)
        # Данные для таблицы
        self.CREDENTIALS_FILE = 'coursewatcherpy-aff762dfc485.json'
        self.spreadsheetId = '1UQpOEjhkNcd-TVqIuXcK00Q3JeR_YJyhj4IbTVhSODU'
        # настройка браузера Google
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=options)

    """
        Получение текущей валюты
    """

    def price_out(self):
        timestamp = datetime.datetime.now()
        desk_name = self.driver.find_elements(By.XPATH, '//span[@class="desktop-name ng-binding"]')
        wallet_value = self.driver.find_elements(By.CLASS_NAME, 'price')[1]
        for i in desk_name:
            print(i.text)
        print(wallet_value.text)
        return (timestamp.strftime('%H:%M - %m.%d.%Y'),desk_name[0].text, wallet_value.text)

    """
        Выгрузка в гугл таблицы
    """

    def add_in_google(self,values_data:list):
        print('[INFO] Работаю с таблицей Google')
        # Рабочая таблица https://docs.google.com/spreadsheets/d/1UQpOEjhkNcd-TVqIuXcK00Q3JeR_YJyhj4IbTVhSODU
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
        print(sheet_values)
        sheet_values.append(values_data)
        results = service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "1 list!A1:D3",
                "majorDimension": "ROWS",
                "values": [
                            sheet_values
                        ]}
            ]
        }).execute()
        print('[INFO] Работа с Google таблицей завершена')
    
    """
        Получение скриншота из браузера
    """
    def screen(self, screen_info: webdriver.Chrome.get_screenshot_as_png, name='img'):
        print('[INFO] Делаю скриншот браузера с открытой страницей')
        with open(f'{name}.png', "wb") as fl:
            fl.write(screen_info)
        print('[INFO] Получен снимок браузера')

    """
        Запуск программы
    """

    def run(self):
        url_search = 'https://www.cryptocompare.com'

        self.driver.get(url_search)
        while True:
            self.add_in_google(self.price_out())
            time.sleep(3600)
        else:
            self.driver.quit()


if __name__ == "__main__":
    test = Avito_Watcher()
    test.start()

