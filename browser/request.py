import os

import aiohttp
from requests.sessions import Session
from requests.exceptions import ConnectionError

from core.tg_send import send_telegram_message


class Request():
    def __init__(self):
        pass
    async def _get(self,url,headers=None,proxy=None,cookies=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers,proxy=proxy,cookies=cookies) as response:
                print('url :',url)
                print("Status:", response.status)
                print("headers:", dict(response.headers))
                print("responce cookies",response.cookies)
                html = await response.text()
                await self._save_page(html)
                return html
    def _sync_get(self,url,headers=None,proxy=None,cookies=None):
        session = Session()
        try:
            response = session.get(url,headers=headers,proxies=proxy,cookies=cookies)
        except Exception as e:
            msg = f'Clicker\nConnect error\nproxy {proxy["https"]}\npod {os.environ["HOSTNAME"]}'
            send_telegram_message(msg)
            return 1
        print('url :', url)
        print("Status:", response.status_code)
        print("headers:", dict(response.headers))
        return response


    def _save_page(self,page):
        with open('last.html','w') as writer:
            writer.write(page)
    def create_request(self,url,proxy):
        print(proxy)
        base_headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        proxy = {'http':f'socks5://{proxy["ip"]}:{proxy["port"]}','https':f'socks5://{proxy["ip"]}:{proxy["port"]}'}
        return  self._sync_get(url,base_headers,proxy)


