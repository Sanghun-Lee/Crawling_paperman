from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from xpath import musinsa_xpath as xpath
from datetime import date
from bs4 import BeautifulSoup
import os
import pandas as pd
import time
import re


class Webdriver:
    def __init__(self):
        path = '/Applications/chromedriver'
        options = Options()
        # options.add_argument('headless')    # 창 띄우지 않고 진행
        options.add_argument("--no-sandbox")  # GUI를 사용할 수 없는 환경에서 설정. linux, docker 등
        options.add_argument("--disable-gpu")  # GUI를 사용할 수 없는 환경에서 설정. linux, docker 등
        options.add_argument(f"--window-size={1600, 1600}")
        options.add_argument("--blink-setting=imagesEnable=false")  # 이미지 로딩 안함
        options.add_argument('Content-Type=application/json; charset=utf-8')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15")
        self.driver = webdriver.Chrome(executable_path=path, options=options)
        self.driver.set_window_size(1600, 1600)
        self.driver.implicitly_wait(3)  # 웹 자원 로드 위해 3초 대기


class Musinsa():
    def __init__(self):
        self.driver = Webdriver().driver
        self.url = 'https://www.musinsa.com/app/?skip_bf=Y'

    def link_crawling(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(15)
        self.driver.find_element(By.XPATH, xpath.ranking_xpath).click()
        # today.sleep(1)
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

        # 제목의 경우 빈값이 나오는 경우가 있어서 빈값 제거
        titles_list = list(filter(None, titles_list))
        # 2페이지까지 크롤링 하고 100개만 사용
        titles_list = titles_list[:100]
        urls_list = urls_list[:100]
        # for i in range(len(titles_list)):
        #     print(f"{i}번쨰 : {titles_list[i]}")
        print("전체 상품수 : ", len(titles_list))
        print("전체 링크수 : ", len(urls_list))

        url_df = pd.DataFrame({'title': titles_list, 'url': urls_list})
        # print(url_df)
        Saving.save_csv(url_df)
        print("link_크롤링 완료 및 저장")
        # self.driver.close()

        return url_df

    def main_crawling(self, df):
        url_df = df["url"]
        url_list = len(url_df)
        # print(url_list)

        result_list = []  # 상품별 리뷰를 담아둘 리스트
        # for i in range(url_list):
        for i in range(2):  # 테스트용
            url = url_df[i]
            self.driver.get(url)  # 무신사 리뷰중 스타일 후기 리뷰를 크롤링
            self.driver.implicitly_wait(15)

            # 이벤트 배너 생성시 닫기 클릭
            event_popup = '/html/body/div[15]/div[2]/button'
            print(i)
            if i < 1:
                # if self.driver.find_element(By.XPATH, event_popup):
                self.driver.find_element(By.XPATH, event_popup).click()
                print("이벤트 팝업창 종료")
            else:
                print("이벤트 팝업창 없음")
                pass
            self.driver.implicitly_wait(15)
            time.sleep(1)

            # 리뷰의 전체 페이지 수 확인
            page = self.driver.find_element(By.XPATH, xpath.all_page_xpath).text[:4]
            pages_num = int(page.replace(" ", ''))
            print(f"전체 리뷰 페이지 수 : {pages_num}")

            p = 4  # 페이지 버튼 클릭을 위한 값
            temp_list = []  # 각 페이지 별 리뷰를 담아둘 임시 리스트
            # today.sleep(1)
            # for i in range(pages_num):
            for i in range(3):  ##테스트용
                # BeautifulSoup을 이용한 크롤링
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                self.driver.implicitly_wait(10)
                if soup.find_all("div", class_="review-contents__text"):
                    review = soup.findAll("div", class_="review-contents__text")
                    # print("review\n", review)
                    # findAll의 경우 text를 바로 뽑을수 없어서 반복문을 사용
                    for texts in review:
                        review = texts.text  # str 형태로 가져옴
                        temp_list.append(review)
                    # print("temp_list\n", temp_list)
                else:
                    print("ERROR 해당 페이지에서 상품 리뷰를 찾지 못함")
                    pass

                """""
                # 셀레니움을 이용한 크롤링
                # 한페이지에 10개씩 리뷰가 등장
                for j in range(1, 11):
                    review_xpath = f'//*[@id = "reviewListFragment"] / div[{j}] / div[4] / div[1]'
                    today.sleep(0.4)
                    review = self.driver.find_element(By.XPATH, review_xpath).text
                    temp_list.append(review)
                    # print(review)
                """""

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
                    print("리뷰 페이지 끝")
                    pass
                print(f"temp_lsit :  {len(temp_list)}\n")
            result_list.append(temp_list)
        print(f"result_list :  {len(result_list)}\n")
        result = pd.DataFrame({'text': result_list})
        print(result)
        self.driver.close()

        return result


class Saving():
    def __init__(self):
        self.time = date.today().isoformat()
        self.link_csv_name = f"musinsa_link_{self.time}"
        self.finish_csv_name = f"musinsa_{self.time}"

    def save_csv(self, result_df):
        df = result_df
        # 칼럼 길이가 3개 미만일시에 url 수집으로 판단
        if len(df.columns) <= 2:
            df.to_csv(f'./files/{self.link_csv_name}.csv', encoding='utf-8')
        else:
            df.to_csv(f'./files/{self.finish_csv_name}.csv', encoding='utf-8')
        return df

    def csv_merge(self, df, result):
        # 크롤링 결과를 dataframe 변경 후 기존 datafream과 병합
        result_df = pd.merge(df, result, left_index=True, right_index=True, how='left')
        print(result_df)
        # result.to_csv(f'{self.finish_csv_name}', encoding='utf-8')
        self.save_csv(result_df)
        print("csv 저장 완료")


class main:
    musinsa = Musinsa()
    save = Saving()
    print("무신사 크롤링 시작")
    start_time = time.time()
    today = date.today().isoformat()
    url_file = f'./files/musinsa_link_{today}.csv'
    if os.path.isfile(url_file):
        print('url 완료 파일 존재')
        first_df = pd.read_csv(f'./files/musinsa_link_{today}.csv', index_col=0)
    else:
        print('url 수집 시작')
        first_df = musinsa.link_crawling()  # url 수집 파일이 없을시
    result_df = musinsa.main_crawling(first_df)
    save.csv_merge(first_df, result_df)
    print(f"무신사 크롤링 종료 \n 소요 시간 : {time.time() - start_time}")


if __name__ == "__main__":
    main

