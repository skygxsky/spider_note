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
        self.max_hosts = ['',0] # [host: url_count] 目前pool中url最多的host及其url数量
        self.hub_pool = {} #{url: last_query_time, }  存放hub url
        self.hub_refresh_span = 0
        self.load_cache()

    def __del__(self):
        self.dump_cache()

    def load_cache(self):
        """
        读
        :return:
        """
        path = self.name + '.pkl'
        try:
            with open(path,'rb') as f:
                self.waiting = pickle.load(f)
            cc = [len(v) for k,v in self.waiting.items()]
            print('saved pool loaded! urls:',sum(cc))
        except:
            pass

    def dump_cache(self):
        """
        写
        :return:
        """
        path = self.name + '.pkl'
        try:
            with open(path,'wb') as f:
                pickle.dump(self.waiting,f) #将对象obj保存到文件file中
            print('self.waiting saved')
        except:
            pass

    def set_hub(self,urls, hub_refresh_span):
        self.hub_refresh_span = hub_refresh_span
        self.hub_pool = {}
        for url in urls:
            self.hub_pool[url] = 0

    def set_status(self,url,status_code):
        if url in self.pending:
            self.pending.pop(url)
        if status_code == 200:
            self.db.set_success(url)
            return
        if status_code == 404:
            self.db.set_success(url)
        if url in self.failure:
            # 重复3次
            self.failure[url] += 1
            if self.failure[url] > self.failure_threshold:
                self.db.set_failure(url)
                self.failure.pop(url)
            else:
                self.add(url)
        else:
            self.failure[url] = 1
            self.add(url)

    def push_to_pool(self,url):
        host = urlparse.urlparse(url).netloc # 域名（netloc）
        if not host or '.' not in host:
            print('bad url:%s'%(str(url)))
            return False
        if host in self.waiting:
            if url in self.waiting[host]:
                return True
            self.waiting[host].add(url)
            if len(self.waiting[host]) > self.max_host[1]:
                self.max_host[0] = host
                self.max_host[1] = len(self.waiting[host])
        else:
            self.waiting[host] = set([url])
        self.waiting_count += 1
        return True

    def add(self,url,always=False):
        if always:
            return self.push_to_pool(url)
        pended_time = self.pending.get(url,0)
        if time.time() - pended_time < self.pending_threshold:
            print('%s is downloading' % (str(url)))
            return
        if self.db.has(url):
            return
        if pended_time:
            self.pending.pop(url)
        return self.push_to_pool(url)

    def add_many(self,urls,always=False):
        if isinstance(urls,str):
            print('urls is a str,must be list',urls)
        else:
            for url in urls:
                self.add(url)

    def pop(self,count, hub_percent=50):
        print('\n\tmax of host :',self.max_hosts)
        # url 两种类型：hub=1,普通=0
        url_attr_url = 0
        url_attr_hub = 1
        # 取出hub，保证hub里面最新url
        hubs = {}
        hub_count = count * hub_percent // 100
        for hub in self.hub_pool:
            span = time.time() - self.hub_pool[hub]
            if span < self.hub_refresh_span:
                continue
            hubs[hub] = url_attr_hub
            self.hub_pool[hub] = time.time()
            if len(hubs) >= hub_count:
                break
        # 取出普通url
        left_count = count - len(hubs)
        urls = {}
        for host in self.waiting:
            if not self.waiting[host]:
                continue
            url = self.waiting[host].pop()
            urls[url] = url_attr_url
            self.pending[url] = time.time()
            if self.max_hosts[0] == host:
                self.max_hosts[1] -= 1
            if len(urls) >= left_count:
                break
        self.waiting_count -= len(urls)
        print('To pop:%s, hubs: %s, urls: %s, hosts:%s' % (count, len(hubs), len(urls), len(self.waiting)))
        urls.update(hubs)
        return urls

    def size(self):
        return self.waiting_count

    def empty(self):
        return self.waiting_count == 0