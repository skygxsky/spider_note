import requests
import execjs

session = requests.session()

with open(r'C:\Users\Administrator\Desktop\工作\crawl\spider_note\04-js逆向\challenge\test2\test2.js','r') as f:
    res = f.read()
    result = execjs.compile(res).call('sdk_2')


cookies = {
    'sessionid': 'qfx2lgcgkaynyn04ib17g2aiiyorhv9x',
    'sign': str(result).split(';')[0].replace('sign=','')
}
response = session.get('http://www.python-spider.com/challenge/2',cookies=cookies)
print(response.content.decode())