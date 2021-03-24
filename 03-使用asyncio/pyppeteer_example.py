import asyncio
import ssl
from pyppeteer import launch
import asyncio
import re
from loguru import logger

ssl._create_default_https_context = ssl._create_unverified_context

class Rotate:

    def __init__(
            self, user_id, user_name, user_password,
            width, height, model_path, mysql
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.user_password = user_password
        self.width = width
        self.height = height
        self.model_path = model_path
        self.mysql = mysql
        self.browser = None

    def __del__(self):
        if self.browser:
            self.browser.close()

    def run(self):
        logger.debug(f'process {self.user_id}.{self.user_name}')
        asyncio.get_event_loop().run_until_complete(self.crack())

    @staticmethod
    async def page_evaluate(page):
        """
        反爬js
        """
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } });window.screen.width=1366; }''')
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {}, };}''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    @staticmethod
    async def get_cookie(page):
        cookies_list = await page.cookies()
        cookies = ''
        for cookie in cookies_list:
            str_cookie = '{0}={1};'
            str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
            cookies += str_cookie
        return cookies

    async def crack(self):
        self.browser = await launch(
            {
                'headless': False,
                'slowMo': 1.3,
                'args': [
                    f'--window-size={self.width},{self.height}'
                    '--disable-extensions',
                    '--hide-scrollbars',
                    '--disable-bundled-ppapi-flash',
                    '--mute-audio',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-infobars'
                ],
                'dumpio': True
            }
        )
        page = await self.browser.newPage()
        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        await page.setViewport({'width': self.width, 'height': self.height})
        await self.page_evaluate(page)
        await page.goto('http://feedads.baidu.com/nirvana/main.html')
        await page.waitFor(5000)
        await page.waitForSelector(
            '#app > div.inner-wrap > div.row.slider-login > div.login.pull-right > div.login-header > span')
        await page.click(
            '#app > div.inner-wrap > div.row.slider-login > div.login.pull-right > div.login-header > span')
        await asyncio.sleep(2)
        await page.type('#uc-common-account', self.user_name)
        await asyncio.sleep(0.5)
        await page.type('#ucsl-password-edit', self.user_password)
        await page.click("#submit-form")
        await asyncio.sleep(5)
        rot_img = await page.querySelector('.vcode-spin-img')
        # 如果有验证码就去旋转
        if rot_img:
            while rot_img:
                img_url = await (await(rot_img).getProperty("src")).jsonValue()
                angle = process_images(img_url, self.model_path)
                bottom_line = await (
                    await(await page.querySelector(".vcode-spin-bottom")).getProperty("offsetWidth")).jsonValue()
                button_line = await (
                    await(await page.querySelector(".vcode-spin-button")).getProperty("offsetWidth")).jsonValue()
                b = bottom_line - button_line
                move_line = angle / 360 * b
                await self.try_validation(page, move_line)
                await asyncio.sleep(3)
                rot_img = await page.querySelector('.vcode-spin-img')
                login_codes = await page.querySelector('.one-ui-pro-nav-logo > img[src]')
                if login_codes:
                    break
        cookies1 = await self.get_cookie(page)
        user_id = re.findall('CPID_3=(\d+)', cookies1)[0]
        token = re.findall('CPTK_3=(\d+)', cookies1)[0]
        await page.goto('https://caiwu.baidu.com')
        cookies2 = await self.get_cookie(page)
        await page.waitFor(2000)
        await page.goto('https://tuiguang.baidu.com/')
        await asyncio.sleep(3)
        await asyncio.wait([
            page.waitForNavigation(),
            page.goto('https://tuiguang.baidu.com/'),
        ])
        await page.waitFor(5000)
        await page.waitFor(2000)
        await page.click(
            '#root-container > div > div.main-document > div.services-container.is-not-kacrm > div > div:nth-child(2) > span > span:nth-child(1) > img')
        await asyncio.sleep(3)
        page2 = (await self.browser.pages())[2]
        cookies3 = await self.get_cookie(page2)
        logger.debug(f'\n{cookies1}\n{cookies2}\n{cookies3}\n{token}')
        succeed, result = self.mysql.update(
            f"update du_shop_cookie set cookie='{cookies1}',token='{token}',user_id='{user_id}',finacial_cookie='{cookies2}', du_cookie='{cookies3}' where id={self.user_id}"
        )
        if not succeed:
            logger.error(f"\n{result}\naccount {self.user_id}.{self.user_name}.{user_id} save cookie to database error")
        await self.browser.close()

    @staticmethod
    async def try_validation(page, distance=308):
        # 将距离拆分成两段，模拟正常人的行为
        distance1 = distance - 10
        distance2 = 10
        btn_position = await page.evaluate('''
           () =>{
            return {
             x: document.querySelector('.vcode-spin-button').getBoundingClientRect().x,
             y: document.querySelector('.vcode-spin-button').getBoundingClientRect().y,
             width: document.querySelector('.vcode-spin-button').getBoundingClientRect().width,
             height: document.querySelector('.vcode-spin-button').getBoundingClientRect().height
             }}
            ''')
        x = btn_position['x'] + btn_position['width'] / 2
        y = btn_position['y'] + btn_position['height'] / 2
        # print(btn_position)
        await page.mouse.move(x, y)
        await page.mouse.down()
        await page.mouse.move(x + distance1, y, {'steps': 30})
        await page.waitFor(800)
        await page.mouse.move(x + distance1 + distance2, y, {'steps': 20})
        await page.waitFor(800)
        await page.mouse.up()
