import threading
from loguru import logger
import time
import pandas as pd
from sqlalchemy import create_engine


class ApiDataThread(object):

    def __init__(self,shop_info_list):

        self.shop_info_list = shop_info_list
        self.thread_lock = threading.Lock()

    def get_info(self):
        task = None
        self.thread_lock.acquire()
        if self.shop_info_list:
            task = self.shop_info_list.pop()
            """
            取数据
            """
        self.thread_lock.release()
        if task is not None:
            """
            业务逻辑
            """

            self.thread_lock.acquire()
            """
            存储数据
            """
            self.thread_lock.release()


    def main(self,n):
        pool = []
        for i in range(n):
            t = threading.Thread(target=self.get_info)
            t.start()
            pool.append(t)
        for j in pool:
            j.join()

if __name__ == '__main__':
    obj = ApiDataThread(list)
    obj.main(len(list))
