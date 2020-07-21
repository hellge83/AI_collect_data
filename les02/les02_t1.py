# -*- coding: utf-8 -*-
# =============================================================================
# 1) Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# 
# *Наименование вакансии
# *Предлагаемую зарплату (отдельно мин. и отдельно макс. и отдельно валюта)
# *Ссылку на саму вакансию        
# *Сайт откуда собрана вакансия
# По своему желанию можно добавить еще работодателя и расположение. Данная структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
# 
# =============================================================================
from bs4 import BeautifulSoup as bs
import requests
# import json
import pandas as pd
import numpy as np

def hh_request(page):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    url = 'https://hh.ru/search/vacancy'
    params = {'L_is_autosearch': 'false',
             'clusters': 'true',
             'enable_snippets': 'true',
             'search_field': 'name',
             'text': vacancy,
             'page': page,
    }
    response = requests.get(url, headers = headers, params = params)
    return response

def hh_page_vac(page):
    hh_vac = []
    hh_response = hh_request(page)
    hh_soup = bs(hh_response.text, 'lxml')
    hh_vacancies = hh_soup.find_all('div', {'class': 'vacancy-serp-item', })

    for vacancy in hh_vacancies:
        vacancy_data = {}
        vacancy_data['source'] = 'headhunter'
        vacancy_data['name'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
        vacancy_data['url'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
        if not vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}):
            vacancy_data['salary'] = ''
            vacancy_data['min_salary'] = ''
            vacancy_data['max_salary'] = ''
            vacancy_data['currency'] = ''
        else:
            vacancy_data['salary'] = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
            vacancy_data['currency'] = vacancy_data['salary'][vacancy_data['salary'].rindex(' ') + 1:]
            if vacancy_data['salary'].find('от ') == 0:
                vacancy_data['min_salary'] = vacancy_data['salary'][vacancy_data['salary'].index(' ') + 1 : vacancy_data['salary'].rindex(' ')]
                vacancy_data['max_salary'] = ''
            elif vacancy_data['salary'].find('до ') == 0:
                vacancy_data['min_salary'] = ''
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index(' ') + 1 : vacancy_data['salary'].rindex(' ')]
            else:
                vacancy_data['min_salary'] = vacancy_data['salary'][:vacancy_data['salary'].index('-')]
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('-') + 1 : vacancy_data['salary'].rindex(' ')]
        del vacancy_data['salary']
        # if vacancy_data
        hh_vac.append(vacancy_data)
        
    return(hh_vac)
    
def sj_main_request():
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    url = 'https://russia.superjob.ru/vacancy/search/'
    params = {
              'keywords': vacancy,
              # 'page': page,
    }
    response = requests.get(url, headers = headers, params = params)
    
    # sj_main_response = sj_main_request()
    url = response.url
    page = bs(response.text, 'lxml')
    if page.find_all('div', {'class': '_3zucV L1p51 undefined _2guZ- _GJem'}):
        maxpage = int(page.find_all('div', {'class': '_3zucV L1p51 undefined _2guZ- _GJem'})[0].findChildren(recursive = False)[-2].getText())
    else:
        maxpage = 1
    return url, maxpage
 
def sj_request(page):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    url = sj_url
    params = {
              'page': page,
    }
    response = requests.get(url, headers = headers, params = params)
    return response

def sj_page_vac(page):
    sj_vac = []
    sj_response = sj_request(page)
    sj_soup = bs(sj_response.text, 'lxml')
    sj_vacancies = sj_soup.find_all('div', {'class': 'iJCa5 f-test-vacancy-item _1fma_ _1JhPh _2gFpt _1znz6 _2nteL', })
    
    for vacancy in sj_vacancies:
        vacancy_data = {}
        vacancy_data['source'] = 'superjob'
        vacancy_data['name'] = vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'}).findChild().getText()
        vacancy_data['url'] = 'https://russia.superjob.ru' + vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'}).findChild()['href']
        if vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText() == 'По договорённости':
            vacancy_data['salary'] = ''
            vacancy_data['min_salary'] = ''
            vacancy_data['max_salary'] = ''
            vacancy_data['currency'] = ''
        else:
            vacancy_data['salary'] = vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText()
            # vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
            vacancy_data['currency'] = vacancy_data['salary'][vacancy_data['salary'].rindex('\xa0') + 1:]
            if vacancy_data['salary'].find('от\xa0') == 0:
                vacancy_data['max_salary'] = ''
                vacancy_data['min_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('\xa0') + 1 : vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['min_salary'] = vacancy_data['min_salary'].replace('\xa0', '')
            elif vacancy_data['salary'].find('до\xa0') == 0:
                vacancy_data['min_salary'] = ''
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('\xa0') + 1 : vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['max_salary'] = vacancy_data['max_salary'].replace('\xa0', '')
            else:
                vacancy_data['salary'] = vacancy_data['salary'][:vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
                vacancy_data['min_salary'] = vacancy_data['salary'][:vacancy_data['salary'].index('—')]
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('—') + 1 :]
        del vacancy_data['salary']
        sj_vac.append(vacancy_data)
        
    return(sj_vac)

vacancy = 'царь'
# vacancy = 'аналитик'
# vacancy = input('input vacancy for search:\n')    


hh_main_response = hh_request(0)
hh_page = bs(hh_main_response.text, 'lxml')
if hh_page.find_all('a', {'class': 'bloko-button HH-Pager-Control'}):
    hh_maxpage = int(hh_page.find_all('a', {'class': 'bloko-button HH-Pager-Control'})[-1].getText()) - 1
else:
    hh_maxpage = 0

hh_final = []
# for i in range(hh_maxpage):
for i in range(2):
    hh_final += hh_page_vac(i)


sj_url, sj_maxpage = sj_main_request()

sj_final = []
# for i in range(1, sj_maxpage + 1):
for i in range(1,3):
    sj_final += sj_page_vac(i)


vacancies_list = hh_final + sj_final
vacancies = pd.concat([pd.DataFrame.from_dict(vacancies_list[itm], orient='index').T for itm in range(len(vacancies_list))])

vacancies.loc[vacancies['min_salary'] != '', 'min_salary'] = vacancies.loc[vacancies['min_salary'] != '', 'min_salary'].astype(int)
vacancies.loc[vacancies['max_salary'] != '', 'max_salary'] = vacancies.loc[vacancies['max_salary'] != '', 'max_salary'].astype(int)
vacancies.loc[vacancies['min_salary'] == '', 'min_salary'] = np.nan
vacancies.loc[vacancies['max_salary'] == '', 'max_salary'] = np.nan