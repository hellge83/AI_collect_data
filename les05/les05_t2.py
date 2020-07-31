# -*- coding: utf-8 -*-
"""
Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары

"""
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
import json
from pymongo import MongoClient

def insert_new_data(data, collection):
    for itm in data:
        collection.update_one({'productId': itm['productId']}, {'$set': itm}, upsert = True)

chrome_options = Options()
chrome_options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')
bestsellers = driver.find_element_by_xpath("//div[contains(text(),'Хиты продаж')]/../../../div[@class='gallery-layout sel-hits-block ']")

button_end = None
# while True:
while not button_end:    
    try:
        
        button = WebDriverWait(bestsellers, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="next-btn sel-hits-button-next"]'))
        )
        button.click()
    except exceptions.TimeoutException:
        try:
            button_end = WebDriverWait(bestsellers, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="next-btn sel-hits-button-next disabled"]'))
            )
            button.click()
        except (exceptions.NoSuchElementException, exceptions.ElementClickInterceptedException):
            print('Scrapper error')
            break

items = []   
goods = bestsellers.find_elements_by_css_selector('li.gallery-list-item')
for good in goods:
    item = json.loads(good.find_element_by_css_selector('a.sel-product-tile-title').get_attribute('data-product-info'))
    items.append(item)
    
driver.close()   

client = MongoClient('localhost', 27017)
db = client['mvideo_db']

insert_new_data(items, db.mvideo)