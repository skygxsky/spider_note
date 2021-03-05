import pickle
import redis
import time
import urllib.parse as urlparse
import zlib
import farmhash
import traceback
import pymysql
import logging
import time
import functions as fn
import config
import requests
import cchardet

class MyDownloader(object):

    @classmethod
    def downloader(cls,url,timeout=10,headers=None,debug=False,binary=False):
        """
        :param url:
        :param timeout:
        :param headers:
        :param debug:
        :param binary: 请求结果是图片…………
        :return:
        """
        _headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        redirected_url = url # 重定向
        if headers:
            _headers = headers
        try:
            response = requests.get(url,headers=_headers,timeout=timeout)
            if binary:
                html = response.content
            else:
                encoding = cchardet.detect(response.content)['encoding']
                html = response.content.decode(encoding)
            status = response.status_code
            redirected_url = response.url
        except:
            if debug:
                traceback.print_exc()
            message = 'failed downloads:%s'%(url)
            print(message)
            if binary:
                html = b''
            else:
                html = ''
            status = 0
        return status,html,redirected_url

class MySqlHelper(object):
    """
    max_idle_time 数据库连接时长
    """
    def __init__(self,host,database,user=None,password=None,port=3306,
                 max_idle_time = 7*3600,
                 connect_timeout = 10,
                 time_zone = "+0:00",charset='utf8mb4',sql_mode="TRADITIONAL"
                 ):
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)

        args = dict(use_unicode=True,charset=charset,database=database,
                    init_command="set time_zone = '%s'"%(time_zone),
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=connect_timeout,sql_mode=sql_mode)
        if user is not None:
            args['user'] = user
        if password is not None:
            args['password'] = password

        if "/" in host:
            args['unix_socket'] = host
        else:
            self.socket = None
            pair = host.split(':')
            if len(pair) == 2:
                args['host'] = pair[0]
                args['port'] = int(pair[1])
            else:
                args['host'] = host
                args['port'] = 3306
        if port:
            args['port'] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error('cannot connect to mysql no %s'%(self.host),exc_info=True)

    def _ensure_connected(self):
        if (self._db is None or (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def __del__(self):
        self.close()

    def close(self):
        if getattr(self,"_db",None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        self.close()
        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def query(self,query,*parameters,**kwparameters):
        cursor = self._cursor()
        try:
            cursor.excute(query,kwparameters or parameters)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def get(self,query,*parameters,**kwparameters):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute(self, query, *parameters, **kwparameters):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.lastrowid
        except Exception as e:
            if e.args[0] == 1062:
                pass
            else:
                traceback.print_exc()
                raise e
        finally:
            cursor.close()

    def table_has(self, table_name, field, value):
        if isinstance(value, str):
            value = value.encode('utf8')
        sql = 'SELECT %s FROM %s WHERE %s="%s"' % (
            field,
            table_name,
            field,
            value)
        d = self.get(sql)
        return d

    def table_insert(self, table_name, item):

        fields = list(item.keys())
        values = list(item.values())
        fieldstr = ','.join(fields)
        valstr = ','.join(['%s'] * len(item))
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].encode('utf8')
        sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table_name, fieldstr, valstr)
        try:
            last_id = self.execute(sql, *values)
            return last_id
        except Exception as e:
            if e.args[0] == 1062:
                # just skip duplicated item
                pass
            else:
                traceback.print_exc()
                print('sql:', sql)
                print('item:')
                for i in range(len(fields)):
                    vs = str(values[i])
                    if len(vs) > 300:
                        print(fields[i], ' : ', len(vs), type(values[i]))
                    else:
                        print(fields[i], ' : ', vs, type(values[i]))
                raise e

    def table_update(self, table_name, updates,
                     field_where, value_where):
        '''updates is a dict of {field_update:value_update}'''
        upsets = []
        values = []
        for k, v in updates.items():
            s = '%s=%%s' % k
            upsets.append(s)
            values.append(v)
        upsets = ','.join(upsets)
        sql = 'UPDATE %s SET %s WHERE %s="%s"' % (
            table_name,
            upsets,
            field_where, value_where,
        )
        self.execute(sql, *(values))

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

class NewsSpider(object):

    def __init__(self,name):
        self.db = MySqlHelper(config.Config.db_host,config.Config.db_db,config.Config.username,config.Config.password)
        self.logger = fn.init_file_logger(name + '.log')
        self.urlpool = UrlPool(name)
        self.hub_hosts = None
        self.load_hubs()

    def load_hubs(self):
        sql = 'select url from crawler_hub'
        data = self.db.query(sql)
        self.hub_hosts = set()
        hubs = []
        for i in data:
            host = urlparse.urlparse(i['url']).netloc
            self.hub_hosts.add(host)
            hubs.append(i['url'])
        self.urlpool.set_hub(hubs,300)

    def save_qo_sql(self,url,html):
        urlhash = farmhash.hash64(url)
        sql = 'select url from create_html where urlhash = "%s"'
        d = self.db.get(sql,urlhash)
        if d:
            if d['url'] != url:
                msg = 'farmhash collision:%s <=> %s'%(url,d['url'])
                self.logger.error(msg)
            return True
        if isinstance(html,str):
            html = html.encode('utf-8')
        html_zlib = zlib.compress(html) # 压缩文本
        sql = "insert into crawler_html(urlhash,url,html_zlib) values (%s,%s,%s)"
        good = False
        try:
            self.db.execute(sql,urlhash,url,html_zlib)
            good = True
        except Exception as e:
            if e.args[0] == 1062:
                """重复"""
                good = True
                pass
            else:
                traceback.print_exc()
                raise e
        return good

    def filter_good(self,urls):
        goodlinks = []
        for url in urls:
            host = urlparse.urlparse(url).netloc
            if host in self.hub_hosts:
                goodlinks.append(url)
        return goodlinks

    def process(self,url,ishub):
        status,html,redirected_url = MyDownloader.downloader(url)
        self.urlpool.set_status(url,status)
        if redirected_url != url:
            self.urlpool.set_status(redirected_url,status)
        # 提取hub网页中的链接，新闻网页中也有“相关新闻”的链接，按需求提取
        if status != 200:
            return
        if ishub:
            newlinks = ""
            goodlinks = self.filter_good(newlinks)
            print("%s/%s,goodlinks/newlinks"%(len(goodlinks),len(newlinks)))
            self.urlpool.add_many(goodlinks)
        else:
            self.save_qo_sql(redirected_url,html)

    def run(self):
        while 1:
            urls = self.urlpool.pop(5)
            for url,ishub in urls.items():
                self.process(url,ishub)
if __name__ == '__main__':
    crawler = NewsSpider('name')
    crawler.run()
