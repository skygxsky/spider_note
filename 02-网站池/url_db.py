import redis

r = redis.Redis(host='localhost',port=6379,db=0)
# r.set('guo','shuai')
# r.set('guo','shuai1')
r.rpush('k1','a','b')
# print(r.get('guo'))
print(r.lrange('k1',0,-1))
# 多少条数据
# print(r.dbsize())
# 清空r中的shuju
# r.flushdb()

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