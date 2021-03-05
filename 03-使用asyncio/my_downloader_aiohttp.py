import aiohttp
import asyncio
from datetime import datetime

async def fetch(session,url,headers=None,timeout=9):
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    }
    if _headers:
        _headers = headers
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
        msg = 'failed download:%s|exception:%s,%s'%(url,str(type(e)),str(e))
        print(msg)
        html = ''
        status = 0
        redirected_url = url
    return status,html,redirected_url

async def main(urls):
    async with aiohttp.ClientSession() as client:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(fetch(client,url)))
        await asyncio.wait(tasks)
        # status,html,redirected_url = await fetch(client, url, headers=None, timeout=9)
        # return status,html,redirected_url
if __name__ == '__main__':
    urls = []
    print(asyncio.get_event_loop().run_until_complete(main(urls)))