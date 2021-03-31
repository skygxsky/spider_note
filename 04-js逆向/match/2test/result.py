import execjs

with open(r'C:\Users\Administrator\Desktop\工作\crawl\spider_note\04-js逆向\match\2test\1test.js','r') as f:
    text = f.read()
    # print(text)
    result = execjs.compile(text).call('sdk_crack')
    print(result)