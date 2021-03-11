import aiohttp
from loguru import logger
import asyncio

class AioHttps(object):

    def __init__(self,urls):
        self.urls = urls

    async def fetch(self,session,url,headers=None,timeout=9):
        _headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
        }
        if _headers:
            _headers = headers
        logger.debug('开始请求url%s'%(url))
        try:
            async with session.get(url,headers=_headers,timeout=timeout) as response:
                status = response.status
                html = await response.read()
                encoding = response.get_encoding()
                if encoding == 'gb2313':
                    encoding = 'gbk'
                html = html.decode(encoding,errors='ignore')
                redirected_url = str(response.url)
        except Exception as e:
            msg = 'failed download:%s|exception:%s,%s' % (url, str(type(e)), str(e))
            logger.error(msg)
            html = ''
            status = 0
            redirected_url = url
        logger.info('请求结束%s'%(url))
        return status, html, redirected_url

    async def main(self):
        async with aiohttp.ClientSession() as client:
            tasks = []
            for url in self.urls:
                tasks.append(asyncio.create_task(self.fetch(client,url)))
            await asyncio.wait(tasks)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.main())

if __name__ == '__main__':
    urls = ['https://www12.baidu.com/1',
            'https://www12.baidu.com/2',
            'https://www12.baidu.com/3']
    obj = AioHttps(urls)
    obj.run()


