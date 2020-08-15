import scrapy
from scrapy.http import HtmlResponse
from instagram.items import InstagramItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstaparserSpider(scrapy.Spider):
    name = 'instaparser'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    
    insta_login = ''
    insta_pwd = ''
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    
    parse_user = ['skydivecats', 'hellge.fly']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    
    config = [{'query_hash': 'c76146de99bb02f6415203be841dd25a', 'path': 'edge_followed_by'},
              {'query_hash': 'd04b0a864b4b54837c0d870b0e77e076', 'path': 'edge_follow'}]

    
    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method = 'POST',
            callback = self.user_parse,
            formdata = {'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers = {'X-CSRFToken': csrf_token}
        )
    
    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for self.usr in self.parse_user:
                yield response.follow(
                    f'/{self.usr}',
                    callback = self.user_data_parse,
                    cb_kwargs = {'username': self.usr}
            )


    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables={'id': user_id,
                'include_reel': 'true',
                'fetch_mutual': 'true',
                'first': 50,
                }
        for self.itm in self.config:
            config_path = self.itm['path']
            config_hash = self.itm['query_hash']
            url_list = f"{self.graphql_url}query_hash={config_hash}&{urlencode(variables)}"
            
            if self.itm['path'] == 'edge_followed_by':
                method = self.edge_followed_by
            else:
                method = self.edge_follow
                
            yield response.follow(
                url_list,
                callback = method,
                cb_kwargs = {'username':username,
                             'user_id':user_id,
                             'config_path': deepcopy(config_path),
                             'config_hash': deepcopy(config_hash),
                             'variables':deepcopy(variables)}
            )

    def edge_followed_by(self, response:HtmlResponse, username, user_id, config_path, config_hash, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get(config_path).get('page_info')   
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_list = f'{self.graphql_url}query_hash={config_hash}&{urlencode(variables)}'
            yield response.follow(
                url_list,
                callback=self.edge_followed_by,
                cb_kwargs = {'username':username,
                             'user_id':user_id,
                             'config_path': deepcopy(config_path),
                             'config_hash': deepcopy(config_hash),
                             'variables':deepcopy(variables)}
            )
        users = j_data.get('data').get('user').get(config_path).get('edges')
        for user in users:
            item = InstagramItem(
                user_id = user_id,
                utype = config_path,
                uid = user['node']['id'],
                username = user['node']['username'],
                photo = user['node']['profile_pic_url'],
            )
            yield item  
    
    
    def edge_follow(self, response:HtmlResponse, username, user_id, config_path, config_hash, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get(config_path).get('page_info')   
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_list = f'{self.graphql_url}query_hash={config_hash}&{urlencode(variables)}'
            yield response.follow(
                url_list,
                callback=self.edge_follow,
                cb_kwargs = {'username':username,
                             'user_id':user_id,
                             'config_path': deepcopy(config_path),
                             'config_hash': deepcopy(config_hash),
                             'variables':deepcopy(variables)}
            )
        users = j_data.get('data').get('user').get(config_path).get('edges')
        for user in users:
            item = InstagramItem(
                user_id = user_id,
                utype = config_path,
                uid = user['node']['id'],
                username = user['node']['username'],
                photo = user['node']['profile_pic_url'],
            )
            yield item 



    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')