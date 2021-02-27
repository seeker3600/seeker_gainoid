from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import os
import chromedriver_binary


class OgiriGenerator:
    def __init__(self):
        options = Options()
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=500,1024")
        options.add_argument("--allow-file-access-from-files")
        options.add_argument("--lang=ja-JP")

        self.options = options
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("about:blank")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()

    def quit(self):
        self.driver.quit()

    def gen(self, embed_html):

        self.load_embed_html(embed_html)
        png = self.html_to_png()

        return png

    def load_embed_html(self, embed_html):
        driver = self.driver
        embed_html = embed_html.replace("\n", "").replace("\r", "")

        driver.execute_script(
            f"""
            let div = document.getElementById('entry');
            if(div)
            {{
                div.innerHTML = '{embed_html}';
                await twttr.widgets.load();
                return;
            }}

            div = document.createElement('div');
            div.setAttribute('id', 'entry');
            div.innerHTML = '{embed_html}';
            document.body.appendChild(div);

            let js = document.createElement('script');
            js.setAttribute('src', 'https://platform.twitter.com/widgets.js');
            document.body.appendChild(js);
        """
        )

    JAVASCRIPTISLOADEDALLIMAGESDEFINE = """
        window.isLoadedAllImages = () => {
            const images = document.getElementsByTagName("img");
            let completed = true;
            for (const image of images) {
                if (image.complete === false) {
                completed = false;
                break;
                }
            }
            return completed;
        };
        window.getRandomInt = (min, max) => {
            min = Math.ceil(min);
            max = Math.floor(max);
            return Math.floor(Math.random() * (max - min) + min);
        };
        window.strIns = (str, idx, val) => {
            return str.slice(0, idx) + val + str.slice(idx);
        };
    """

    def html_to_png(self):
        driver = self.driver

        # まずはフレームに入る
        iframe = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element_by_tag_name("iframe"),
        )
        driver.switch_to.frame(iframe)

        # カード生成の完了まで待機
        WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_element_by_css_selector("article > div > div > span"),
        )

        # 画像の読み込み完了まで待機
        driver.execute_script(self.JAVASCRIPTISLOADEDALLIMAGESDEFINE)
        WebDriverWait(driver, timeout=3).until(
            lambda d: d.execute_script("return isLoadedAllImages();"),
        )

        # テキストを書き換え
        # "document.querySelector('article > div > div > span').textContent='yeah';"
        # str = str.replace(/(?<=^.{3}).{3}/, "■■■")
        driver.execute_script(
            """
            const span = document.querySelector('article > div > div > span');
            const beforeLen = span.textContent.length;

            do {
                let str = span.innerHTML;
                const start = getRandomInt(0, str.length - 1);
                const len = Math.min(getRandomInt(1, str.length - start), Math.ceil(str.length / 5));

                str = strIns(str, start + len, "</span>");
                str = strIns(str, start, "<span style='background-color: white; color: white;'>");
                
                span.innerHTML = str;
            } while(beforeLen !== span.textContent.length);
            """
        )

        # 内容を確認
        # span = driver.find_element_by_css_selector("article > div > div > span")
        # print(span.text)

        # カードのスクショを返却
        card = driver.find_element_by_id("app")
        png = card.screenshot_as_png

        driver.switch_to.default_content()
        return png


if __name__ == "__main__":
    embed = """<blockquote class="twitter-tweet" data-lang="ja-JP" data-theme="dark"><p lang="ja" dir="ltr">理也ちゃん、モルカ―作れないかなあ</p>&mdash; 森いちご (@strawberry_fore) <a href="https://twitter.com/strawberry_fore/status/1358400871638261764?ref_src=twsrc%5Etfw">2021年2月7日</a></blockquote>"""

    try:
        os.remove("screenshot.png")
    except:
        pass

    with OgiriGenerator() as generator:
        png = generator.gen(embed)
        png = generator.gen(embed)

        with open("screenshot.png", "wb") as f:
            f.write(png)
