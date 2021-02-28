import requests
import cchardet
import traceback

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

if __name__ == '__main__':
    url = 'http://www.baidu.com'
    status,html,redirected_url = MyDownloader.downloader(url)
    print(status,html,redirected_url)