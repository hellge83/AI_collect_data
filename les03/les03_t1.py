# -*- coding: utf-8 -*-
# =============================================================================
# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы. Поиск по двум полям (мин и макс зарплату)
# 3) Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
# =============================================================================
from vacancies import main_scraper
from pymongo import MongoClient


def insert_new_data(data):
    for vac in vacancies_list:
        if not vacancies.find({'_id': vac['_id']}).count():
            vacancies.insert_one(vac)

# vacancy = 'менеджер'
# salary = 150000            
vacancy = input('Input vacancy name:\n')    
salary = int(input('Input min salary:\n')) 
 
vacancies_list = main_scraper(vacancy)

client = MongoClient('localhost', 27017)
db = client['vacancies_db']

vacancies = db[f'{vacancy}']
insert_new_data(vacancies_list)

result = []
# Нужно ли обрабатывать ситуацию, когда max_salary null? min и max обе null?
# Это можно расценить и как больше заданной, и как меньше
for vac in vacancies.find({'$or': [{'min_salary': {'$gt': salary}}, {'max_salary': {'$gt': salary}}]}, {'name': 1, 'min_salary': 1, 'max_salary': 1, '_id': 0, 'url': 1}):
    result.append(vac)

print(result)