# -*- coding: utf-8 -*-
"""
Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

"""
import requests
import json

credentials = {}
with open ('credentials.txt', 'r') as f:
    for line in f:
        key, value = line.split(' = ')
        credentials[key] = value.rstrip('\n')

user_id = int(input('input userid:\n'))

user_get_params = {'user_ids': user_id, 
                      'access_token': credentials['auth_token'],
                      'v': '5.120',
                      'fields': 'sex'
    }
user_get_link = 'https://api.vk.com/method/users.get'
user_get = requests.get(user_get_link, params = user_get_params) 
if user_get.ok:
    username = f"{user_get.json()['response'][0]['first_name']} {user_get.json()['response'][0]['last_name']}"

friends_get_params = {'user_id': user_id, 
                      'order': 'name',
                      'access_token': credentials['auth_token'],
                      'v': '5.120',
                      'fields': 'sex'
    }
friends_get_link = 'https://api.vk.com/method/friends.get'
friends_get = requests.get(friends_get_link, params = friends_get_params)

if friends_get.ok:
    data = friends_get.json()
    with open(str(user_id)+'_friends.json', 'w') as f:
        json.dump(data, f)

   
friend_name = [f"{friend['first_name']} {friend['last_name']}" for friend in data['response']['items']]    

print(f"{username} friends are\n: {friend_name}")