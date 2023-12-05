import random

import requests

from core.config import PROXY_URL


class Proxy():
    def __init__(self):
        self.base_url = PROXY_URL
        self.session_id = ''.join(
            [random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(12)])

    def get_request(self,path,params=None):
        url = self.base_url + path
        return requests.get(url,params=params, verify=False)

    def put_request(self,path,params=None):
        url = self.base_url + path
        return requests.put(url,params=params, verify=False)

    def get_proxy(self,country):
        path = '/'
        params = {'country':country,'container_number':self.session_id}
        return self.get_request(path,params=params)

    def add_error(self,id_proxy):
        path = '/add_error'
        params = {'id': id_proxy}
        return self.put_request(path,params=params)

    def delete(self,id_proxy):
        path = self.base_url+'/'
        params = {'id': id_proxy}
        return requests.delete(path,params=params, verify=False)
    def release(self,id):
        path = self.base_url + '/release_proxy'
        params = {'id_proxy': id}
        return requests.post(path, params=params, verify=False)









