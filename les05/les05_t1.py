# -*- coding: utf-8 -*-
"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from pymongo import MongoClient

def insert_new_data(data, collection):
    for itm in data:
        collection.update_one({'text': itm['text']}, {'$set': itm}, upsert = True)


chrome_options = Options()
chrome_options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mail.ru/')

username = driver.find_element_by_id('mailbox:login')
username.send_keys('study.ai_172@mail.ru')
username.send_keys(Keys.RETURN)
driver.implicitly_wait(3)

# result = driver.find_element_by_id("saveauth").is_selected()
# if result:
#     pass
# else:
#     driver.find_element_by_id("saveauth").click()
  
password = driver.find_element_by_id('mailbox:password')
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)
driver.implicitly_wait(5)

messages = driver.find_elements_by_class_name('js-letter-list-item')
messages[0].click()

letters = []
exists = None

while not exists:
    try:
        message = {}
        message['from'] = driver.find_element_by_class_name('letter-contact').get_attribute('title')
        message['date'] = driver.find_element_by_class_name('letter__date').text
        message['header'] = driver.find_element_by_class_name('thread__subject').text
        message['text'] = driver.find_element_by_class_name('letter-body__body-content').text
        letters.append(message)
        # driver.implicitly_wait(10)
        next_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[title="Следующее"]'))
        )
        exists = next_msg.get_attribute('disabled')
        next_msg.click()
    except (exceptions.NoSuchElementException, exceptions.TimeoutException, exceptions.StaleElementReferenceException):
        print('error')
        break
driver.close()  

client = MongoClient('localhost', 27017)
db = client['inbox_db']

insert_new_data(letters, db.inbox)    