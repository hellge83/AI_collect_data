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

def hh_request(page, vacancy):
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

def hh_page_vac(page, vacancy):
    hh_vac = []
    hh_response = hh_request(page, vacancy)
    hh_soup = bs(hh_response.text, 'lxml')
    hh_vacancies = hh_soup.find_all('div', {'class': 'vacancy-serp-item', })

    for vacancy in hh_vacancies:
        vacancy_data = {}
        vacancy_data['source'] = 'headhunter'
        vacancy_data['name'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
        vacancy_data['url'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
        vacancy_data['_id'] = 'hh_' + vacancy_data['url'][vacancy_data['url'].rindex('/') + 1 : vacancy_data['url'].rindex('?')]
        if not vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}):
            vacancy_data['salary'] = None
            vacancy_data['min_salary'] = None
            vacancy_data['max_salary'] = None
            vacancy_data['currency'] = None
        else:
            vacancy_data['salary'] = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
            vacancy_data['currency'] = vacancy_data['salary'][vacancy_data['salary'].rindex(' ') + 1:]
            if vacancy_data['salary'].find('от ') == 0:
                vacancy_data['min_salary'] = int(vacancy_data['salary'][vacancy_data['salary'].index(' ') + 1 : vacancy_data['salary'].rindex(' ')])
                vacancy_data['max_salary'] = None
            elif vacancy_data['salary'].find('до ') == 0:
                vacancy_data['min_salary'] = None
                vacancy_data['max_salary'] = int(vacancy_data['salary'][vacancy_data['salary'].index(' ') + 1 : vacancy_data['salary'].rindex(' ')])
            elif vacancy_data['salary'].find('-') == -1:
                vacancy_data['min_salary'] = int(vacancy_data['salary'])
                vacancy_data['max_salary'] = int(vacancy_data['salary'])
            else:
                vacancy_data['min_salary'] = int(vacancy_data['salary'][:vacancy_data['salary'].index('-')])
                vacancy_data['max_salary'] = int(vacancy_data['salary'][vacancy_data['salary'].index('-') + 1 : vacancy_data['salary'].rindex(' ')])
        del vacancy_data['salary']
        # if vacancy_data
        hh_vac.append(vacancy_data)
        
    return(hh_vac)
    
def sj_main_request(vacancy):
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
 
def sj_request(page, url):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    url = url
    params = {'profession_only': 1,
              'page': page,
    }
    response = requests.get(url, headers = headers, params = params)
    return response

def sj_page_vac(page, url):
    sj_vac = []
    sj_response = sj_request(page, url)
    sj_soup = bs(sj_response.text, 'lxml')
    sj_vacancies = sj_soup.find_all('div', {'class': 'iJCa5 f-test-vacancy-item _1fma_ _1JhPh _2gFpt _1znz6 _2nteL', })
    
    for vacancy in sj_vacancies:
        vacancy_data = {}
        vacancy_data['source'] = 'superjob'
        vacancy_data['name'] = vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'}).findChild().getText()
        vacancy_data['url'] = 'https://russia.superjob.ru' + vacancy.find('div', {'class': '_3mfro PlM3e _2JVkc _3LJqf'}).findChild()['href']
        vacancy_data['_id'] = 'sj_' + vacancy_data['url'][vacancy_data['url'].rindex('-') + 1 : vacancy_data['url'].rindex('.')]
        if vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText() == 'По договорённости':
            vacancy_data['salary'] = None
            vacancy_data['min_salary'] = None
            vacancy_data['max_salary'] = None
            vacancy_data['currency'] = None
        else:
            vacancy_data['salary'] = vacancy.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).getText()
            # vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
            vacancy_data['currency'] = vacancy_data['salary'][vacancy_data['salary'].rindex('\xa0') + 1:]
            if vacancy_data['salary'].find('от\xa0') == 0:
                vacancy_data['max_salary'] = None
                vacancy_data['min_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('\xa0') + 1 : vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['min_salary'] = int(vacancy_data['min_salary'].replace('\xa0', ''))
            elif vacancy_data['salary'].find('до\xa0') == 0:
                vacancy_data['min_salary'] = None
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('\xa0') + 1 : vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['max_salary'] = int(vacancy_data['max_salary'].replace('\xa0', ''))
            elif vacancy_data['salary'].find('—') == -1:
                vacancy_data['salary'] = vacancy_data['salary'][:vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')               
                vacancy_data['min_salary'] = int(vacancy_data['salary'])
                vacancy_data['max_salary'] = int(vacancy_data['salary'])
            else:
                vacancy_data['salary'] = vacancy_data['salary'][:vacancy_data['salary'].rindex('\xa0')]
                vacancy_data['salary'] = vacancy_data['salary'].replace('\xa0', '')
                vacancy_data['min_salary'] = vacancy_data['salary'][:vacancy_data['salary'].index('—')]
                vacancy_data['max_salary'] = vacancy_data['salary'][vacancy_data['salary'].index('—') + 1 :]
        del vacancy_data['salary']
        sj_vac.append(vacancy_data)
        
    return(sj_vac)

def main_scraper(vacancy):
    hh_main_response = hh_request(0, vacancy)
    hh_page = bs(hh_main_response.text, 'lxml')
    if hh_page.find_all('a', {'class': 'bloko-button HH-Pager-Control'}):
        hh_maxpage = int(hh_page.find_all('a', {'class': 'bloko-button HH-Pager-Control'})[-1].getText()) - 1
    else:
        hh_maxpage = 0
    
    hh_final = []
    # for i in range(hh_maxpage):
    for i in range(3, 5):
        hh_final += hh_page_vac(i, vacancy)
    
    
    sj_url, sj_maxpage = sj_main_request(vacancy)
    
    sj_final = []
    # for i in range(1, sj_maxpage + 1):
    for i in range(4, 6):
        sj_final += sj_page_vac(i, sj_url)
    
    vacancies_list = hh_final + sj_final
    return vacancies_list


