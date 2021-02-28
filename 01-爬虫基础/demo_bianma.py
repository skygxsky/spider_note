import encodings.idna
import requests
import chardet
import cchardet

response = requests.get('http://www.baidu.com')

print(response.content.decode('utf-8'))
print(response.text.encode('utf-8'))
print(chardet.detect(response.content))
# gb2312 < gdk < gb18030

# 检测中文乱码
test1 = chardet.detect('科技健康你十块钱访问'.encode('gbk'))
print(test1)

test2 = cchardet.detect('科技健康你十块钱访问'.encode('gbk'))
print(test2)