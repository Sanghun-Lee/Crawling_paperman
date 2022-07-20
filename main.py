import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from xpath.musinsa import musinsa_xpath as xpath
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
import pandas as pd


class Webdriver:
    def __init__(self):
        path = '/Applications/chromedriver'
        options = Options()
        options.add_argument("--no-sandbox")  # GUI를 사용할 수 없는 환경에서 설정. linux, docker 등
        options.add_argument("--disable-gpu")  # GUI를 사용할 수 없는 환경에서 설정. linux, docker 등
        # options.add_argument(f"--window-size={1200, 700}")
        options.add_argument('Content-Type=application/json; charset=utf-8')
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15")
        self.driver = webdriver.Chrome(executable_path=path, options=options)
        self.driver.set_window_size(1600, 1600)
        self.driver.implicitly_wait(3)  # 웹 자원 로드 위해 3초 대기


class Musinsa():
    def __init__(self):
        self.time = date.today().isoformat()
        self.driver = Webdriver().driver
        # self.link_csv_name = f"musinsa_link_{self.time}"
        # self.finish_csv_name = f"musinsa_{self.time}"
        self.url = 'https://www.musinsa.com/app/?skip_bf=Y'

    def link_crawling(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(20)
        self.driver.find_element(By.XPATH, xpath.ranking_xpath).click()
        # time.sleep(1)
        self.driver.find_element(By.XPATH, xpath.daily_xpath).click()
        self.driver.implicitly_wait(15)
        time.sleep(1)
        titles = self.driver.find_elements(By.CSS_SELECTOR, ".list_info")
        urls = self.driver.find_elements(By.CSS_SELECTOR, ".img-block")
        time.sleep(1)

        titles_list = []
        urls_list = []
        for i in titles:
            title = i.text
            # print(title)
            titles_list.append(title)
            # if (title != ' ') and (title is not None):
            #     titles_list.append(title)

        for i in urls:
            href = i.get_attribute("href")
            # print(href)
            urls_list.append(href)

        self.driver.find_element(By.XPATH, xpath.second_page).click()
        self.driver.implicitly_wait(20)
        time.sleep(2)
        titles = self.driver.find_elements(By.CSS_SELECTOR, ".list_info")
        urls = self.driver.find_elements(By.CSS_SELECTOR, ".img-block")
        time.sleep(1)

        for j in titles:
            title = j.text
            # print(title)
            titles_list.append(title)
            # if (title != ' ') and (title is not None):
            #     titles_list.append(title)

        for j in urls:
            href = j.get_attribute("href")
            # print(href)
            urls_list.append(href)

        titles_list = list(filter(None, titles_list))
        titles_list = titles_list[:100]
        urls_list = urls_list[:100]
        # for i in range(len(titles_list)):
        #     print(f"{i}번쨰 : {titles_list[i]}")
        print("전체 상품수 : ", len(titles_list))
        print("전체 링크수 : " ,len(urls_list))

        url_df = pd.DataFrame({'title': titles_list, 'url': urls_list})
        # print(url_df)
        # url_df.to_csv(f'{self.link_csv_name}.csv', encoding='utf-8')
        # print("link_크롤링 완료 및 저장")
        self.driver.close()

        return url_df

    def main_crawling(self, df):
        url_df = df["url"]
        url_list = len(url_df)
        # print(url_list)

        result_list = []
        for i in range(len(url_list)):
        # for i in range(2):  # 테스트용
            url = url_df[i]
            self.driver.get(url)
            self.driver.implicitly_wait(15)

            # 리뷰의 페이지 확인
            all_page_xpath = '//*[@id="reviewListFragment"]/div[11]/div[1]'
            page = self.driver.find_element(By.XPATH, all_page_xpath).text[:4]
            pages_num = int(page.replace(" ", ''))
            p = 4
            temp_list = []
            time.sleep(1)
            for i in range(pages_num):
            # for i in range(2):    ##테스트용
                # 한페이지에 10개씩 리뷰가 등장
                for j in range(1, 11):
                    review_xpath = f'//*[@id = "reviewListFragment"] / div[{j}] / div[4] / div[1]'
                    time.sleep(0.4)
                    review = self.driver.find_element(By.XPATH, review_xpath).text
                    temp_list.append(review)
                    # print(review)
                # print("기존 p넘버 : ", p)
                page_xpath = f'//*[@id="reviewListFragment"]/div[11]/div[2]/div/a[{p}]'
                if self.driver.find_element(By.XPATH, page_xpath):
                    self.driver.find_element(By.XPATH, page_xpath).click()
                    # print("다음 리뷰 페이지")
                    # # 리뷰페이지를 넘겨주기 위한 초기화
                    if p != 8:
                        p += 1
                        # print("p넘버 : ", p)
                    else:
                        p = 4
                        # print("p넘버 초기화: ", p)
                else:
                    pass
                print(f"temp_lsit :  {len(temp_list)}\n")
            result_list.append(temp_list)
        print(f"result_list :  {len(result_list)}\n")
        result = pd.DataFrame({'text': result_list})
        self.driver.close()

        return result


class Saving():
    def __init__(self):
        self.link_csv_name = f"musinsa_link_{self.time}"
        self.finish_csv_name = f"musinsa_{self.time}"

    def save_csv(self, df):
        if len(df) < 3:
            df.to_csv(f'{self.link_csv_name}.csv', encoding='utf-8')
        else:
            df.to_csv(f'{self.finish_csv_name}', encoding='utf-8')

    def csv_merge(self, df, result):
        # 크롤링 결과를 dataframe 변경 후 기존 datafream과 병합
        result_df = pd.merge(df, result, left_index=True, right_index=True, how='left')
        print(result_df)
        # result.to_csv(f'{self.finish_csv_name}', encoding='utf-8')
        Saving.save_csv(result_df)
        print("csv 저장 완료")


if __name__=="__main__":
    musinsa = Musinsa()
    save = Saving()
    # first_df = musinsa.link_crawling()
    first_df = pd.read_csv('musinsa_link_2022-07-20.csv', index_col=0)
    result_df = musinsa.main_crawling(first_df)
    save.csv_merge(first_df, result_df)
