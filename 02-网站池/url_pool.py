import pickle
import redis
import time
import urllib.parse as urlparse

class UrlDb(object):

    status_failure = b'0'
    status_success = b'1'

    def __init__(self,host,db_name):
        self.name = db_name + '.urldb'
        self.db = redis.Redis(host=host,port=6379,db=db_name)

    def set_success(self,url):
        if isinstance(url,str):
            url = url.encode('utf8')
        try:
            self.db.set(url,self.status_success)
            s = True
        except:
            s = False
        return s

    def set_failure(self,url):
        if isinstance(url,str):
            url = url.encode('utf8')
        try:
            self.db.set(url,self.status_failure)
            s = True
        except:
            s = False
        return s

    def has(self,url):
        if isinstance(url,str):
            url = url.encode('utf8')
        try:
            attr = self.db.get(url)
            return attr
        except:
            pass
        return False

class UrlPool(object):

    def __init__(self,pool_name):
        self.name = pool_name
        self.db = UrlDb('localhost',pool_name)

        self.waiting = {} #{host: set([urls]), } host分组，记录等待下载的url
        self.pending = {} #{url: pended_time, } 记录已被取出（self.pop()）但还未被更新状态（正在下载）的URL
        self.failure = {} #{url: times,} 记录失败的URL的次数
        self.failure_threshold = 3
        self.pending_threshold = 10 # pending的最大时间，过期要重新下载
        self.waiting_count = 0 # self.waiting里面url的次数
        self.max_host = ['',0] # [host: url_count] 目前pool中url最多的host及其url数量
        self.hub_pool = {}
        self.hub_refresh_span = 0
        self.load_cache()

    def __del__(self):
        self.dump_cache()

    def load_cache(self):
        path = self.name + '.pkl'
        try:
            with open(path,'rb') as f:
                self.waiting = pickle.load(f)
            cc = [len(v) for k,v in self.waiting.items()]
            print('saved pool loaded! urls:',sum(cc))
        except:
            pass

    def dump_cache(self):
        path = self.name + '.pkl'
        try:
            with open(path,'wb') as f:
                pickle.dump(self.waiting,f) #将对象obj保存到文件file中
            print('self.waiting saved')
        except:
            pass