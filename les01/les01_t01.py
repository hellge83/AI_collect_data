# -*- coding: utf-8 -*-
"""
Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
"""
import requests
import json

def build_url(user):
    return f'https://api.github.com/users/{user}/repos'

user = input('user login:\n')

main_link = build_url(user)
response = requests.get(main_link)

if response.ok:
    data = response.json()
    with open(user+'_rep.json', 'w') as f:
        json.dump(data, f)

reps = [data[ind]['name'] for ind in range(len(data))]        
print(reps)