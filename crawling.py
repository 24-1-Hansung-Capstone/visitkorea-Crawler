import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# 크롬 드라이버 실행 및 사이트 접속
driver = webdriver.Chrome()
driver.get("https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms")
driver.maximize_window()
time.sleep(2)

# "서울" 버튼 클릭
seoul_button = driver.find_element(By.XPATH, "//li[@id='1']//button")
seoul_button.click()
time.sleep(2)

# 결과를 저장할 리스트
results = []


# 다음 페이지로 이동하고 데이터 크롤링하는 함수
def go_next_page():
    # "다음" 버튼 클릭
    next_button = driver.find_element(By.XPATH, "//a[@class='btn_next ico']")
    next_button.click()
    time.sleep(2)


def crawl_page():
    # HTML 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # photo 클래스와 area_txt catchphrase 클래스를 가진 요소들 찾기, tag 클래스와 closure 클래스를 가져오고 없다면 빈 문자열 설정.
    for item in soup.find_all('ul', class_='list_thumType place'):
        photo_divs = item.find_all('div', class_='photo')
        area_txt_divs = item.find_all('div', class_='area_txt catchphrase')

        for photo_div, area_txt_div in zip(photo_divs, area_txt_divs):
            photo_url = photo_div.find('img')['src']
            name = area_txt_div.find('div', class_='tit').text.strip()
            location = area_txt_div.find_all('p')[0].text.strip()
            description = area_txt_div.find_all('p')[1].text.strip()

            # p 태그 중 클래스가 "tag"인 요소와 "closure"인 요소 찾기
            tag_elements = area_txt_div.find_all('p', class_='tag')
            closure_elements = area_txt_div.find_all('p', class_='closure')

            # "tag" 클래스가 존재하는 경우 해당 내용을 가져오고, 없는 경우 빈 문자열로 설정
            tags = ' '.join(tag.text.strip() for tag in tag_elements)

            # "closure" 클래스가 존재하는 경우 해당 내용을 가져오고, 없는 경우 빈 문자열로 설정
            closure = ' '.join(closure.text.strip() for closure in closure_elements)

            results.append([name, location, description, tags, closure, photo_url])


# 페이지 번호 초기화
page_num = 1

# 페이지 바에서 "다음" 버튼이 없을 때까지 반복
while True:
    try:
        if page_num == 412:
            crawl_page()
            break
        elif page_num % 5 != 0:
            crawl_page()
            driver.find_element(By.CSS_SELECTOR, f"a[id='{page_num + 1}']").click()
            page_num += 1
            time.sleep(2)
        else:
            crawl_page()
            page_num += 1
            go_next_page()
            time.sleep(2)
    except NoSuchElementException:
        print(f"마지막 페이지까지 크롤링이 완료되었습니다. 총 {page_num} 페이지를 크롤링했습니다.")
        break

# 결과를 CSV 파일에 저장
csv_file = "Visitkorea_Crawled_Data.csv"
with open(csv_file, 'w', newline='', encoding='UTF-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Location", "Description", "Tags", "Closure", "Photo URL"])
    writer.writerows(results)

# 완료 메세지 출력 후 종료
print("모든 데이터 수집 작업이 완료되었습니다.")
