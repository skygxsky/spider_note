import traceback
import time
import asyncio
import aiohttp
import urllib.parse as urlparse
import farmhash
import zlib
import sanicdb
from url_pool import UrlPool
import config
import functions as fn
import my_downloader_aiohttp

class NewsCrawlerAsync(object):

    def __init__(self,name):
        self._workers = 0
        self._workers_max = 30
        self.logger = my_downloader_aiohttp.init_file_logger(name + '.log')
        self.urlpool = UrlPool(name)
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = sanicdb.SanicDB(
            config.db_host,
            config.db_db,
            config.db_user,
            config.db_password,
            loop=self.loop
        )

    async def load_hubs(self):
        sql = 'select url from crawler_hub'
        data = await self.db.query(sql)
        self.hub_hosts = set()
        hubs = []
        for d in data:
            host = urlparse.urlparse(d['url']).netloc
            self.hub_hosts.add(host)
            hubs.append(d['url'])
        self.urlpool.set_hub(hubs,300)

    async def save_to_db(self,url,html):
        urlhash = farmhash.hash64(url)
        sql = 'select url from crawler_html where urlhash=%s'
        d = await self.db.get(sql,urlhash)
        if d:
            if d['url'] != url:
                msg = 'farmhash collision:%s <=> %s'%(url,d['url'])
                self.logger.error(msg)
            return True
        if isinstance(html,str):
            html = html.encode('utf8')
        html_zlib = zlib.compress(html)
        sql = 'insert into crawler_html(urlhash, url, html_lzma) values(%s, %s, %s)'
        good = False
        try:
            await self.db.execute(sql,urlhash,url,html_zlib)
            good = True
        except Exception as e:
            if e.args[0] == 1062:
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

    async def process(self,url,ishub):
        status,html,redirected_url = await my_downloader_aiohttp.fetch(self.session,url)
        self.urlpool.set_status(url,stats)
        if redirected_url != url:
            self.urlpool.set_status(redirected_url,status)
        # 提取hub网页中的链接, 新闻网页中也有“相关新闻”的链接，按需提取
        if status != 200:
            return
        if ishub:
            newlinks = my_downloader_aiohttp.extract_links_re(redirected_url,html)

