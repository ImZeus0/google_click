import asyncio
import datetime
import functools
import os
import threading
import traceback

import pika
from pika.exceptions import ChannelClosedByBroker
from pika.exchange_type import ExchangeType
from requests import JSONDecodeError

import db
from browser.request import Request
from proxy.service_api import Proxy

proxy_service = Proxy()


class AdsQueue():

    def __init__(self,host,exchange,queue,routing_key):
        self.host = host
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key

        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(connection_attempts=1,
                                                                       host=self.host, credentials=credentials,
                                                                       heartbeat=100))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=ExchangeType.direct,
            passive=False,
            durable=True,
            auto_delete=False)

    def on_message(self,ch, method_frame, _header_frame, body, args):
        thrds = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target=self.do_work, args=(ch, delivery_tag, body))
        t.start()
        thrds.append(t)

    def do_work(self,ch, delivery_tag, body):
        try:
            thread_id = threading.get_ident()
            info = body.decode().split('|')
            google_url = info[0]
            country = info[1]
            url = info[2]
            id_project = info[3]
            key = info[4]
            proxy = proxy_service.get_proxy(country)
            if proxy.status_code != 200:
                cb = functools.partial(self.ack_message, ch, delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
                return 0
            try:
                proxy = proxy.json()
                if proxy.get('detail'):
                    print('[X] Error open proxy ', proxy)
                    cb = functools.partial(self.ack_message, ch, delivery_tag)
                    ch.connection.add_callback_threadsafe(cb)
                    return 0
            except JSONDecodeError:
                print('[X] Error open json proxy ', proxy.text)
                cb = functools.partial(self.ack_message, ch, delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
                return 0
            request = Request()
            response = request.create_request(google_url,proxy)
            if response == 1:
                print(f'Error connect {proxy["ip"]}:{proxy["port"]}')
                proxy_service.release(proxy['id'])
                proxy_service.add_error(proxy['id'])
                cb = functools.partial(self.ack_message, ch, delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
                return
            if response.status_code != 200:
                print(f'RESPONCE PROXY {response.status_code} {response.text}')
                proxy_service.release(proxy['id'])
                proxy_service.add_error(proxy['id'])
                cb = functools.partial(self.ack_message, ch, delivery_tag)
                ch.connection.add_callback_threadsafe(cb)
                return
            db.add_click(id_project,country,url,key)
            proxy_service.release(proxy['id'])
            cb = functools.partial(self.ack_message, ch, delivery_tag)
            ch.connection.add_callback_threadsafe(cb)
        except Exception as e:
            print(f'{datetime.datetime.utcnow()}[XXX] main error {str(traceback.format_exc())}')
            proxy_service.release(proxy['id'])
            cb = functools.partial(self.ack_message, ch, delivery_tag)
            ch.connection.add_callback_threadsafe(cb)
            print(f'{datetime.datetime.utcnow()}[X] exit')

    def ack_message(self,ch, delivery_tag):
        """Note that `ch` must be the same pika channel instance via which
        the message being ACKed was retrieved (AMQP protocol constraint).
        """
        if ch.is_open:
            ch.basic_ack(delivery_tag)
        else:
            # Channel is already closed, so we can't ACK this message;
            # log and/or do something that makes sense for your app in this case.
            pass
    def bing(self,queue):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.queue_bind(
            queue=queue, exchange=self.exchange, routing_key=self.routing_key)
        self.channel.basic_qos(prefetch_count=1)
        threads = []
        on_message_callback = functools.partial(self.on_message, args=(threads))
        self.channel.basic_consume(on_message_callback=on_message_callback, queue=queue)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        except Exception as e:
            print(f'{e} date', str(datetime.datetime.now()))

        # Wait for all to complete
        for thread in threads:
            thread.join()

        try:
            self.connection.close()
        except Exception as e:
            print(f'{e} date', str(datetime.datetime.now()))




