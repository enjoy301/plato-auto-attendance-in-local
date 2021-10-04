# 기본 개념 코드의 클래스화
from selenium import webdriver
from datetime import datetime
import time, os , json, sys


time_now = datetime.now()

# 크롬드라이버 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("-start-maximized")
# options.add_argument("--headless")
options.add_argument("--mute-audio")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# pyinstaller 설정 부분
if getattr(sys, 'frozen', False):
    path = os.path.join(sys._MEIPASS, "chromedriver.exe")
    driver = webdriver.Chrome(path, options=options)
else:
    driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)


# json파일 읽어와서 학번 비번 얻기
with open(os.path.join("./", 'secrets.json'), encoding='UTF8') as f:
    secrets = json.loads(f.read())


driver.get('https://plato.pusan.ac.kr/')
driver.find_element_by_id("input-username").send_keys(secrets["학번"])
driver.find_element_by_id("input-password").send_keys(secrets["비밀번호"])
driver.find_element_by_xpath('//*[@id="page-header"]/div[1]/div/div[2]/form/div/input[3]').click()


time.sleep(2)
main_page = driver.find_element_by_xpath('//*[@id="page-container"]')
notice_list = main_page.find_elements_by_css_selector('[class|="modal notice_popup ui-draggable"]')
z_index_list = []
for i in notice_list:
    z_index_list.append(i.value_of_css_property("z-index"))

for i in range(len(notice_list)):
    max_index = z_index_list.index(max(z_index_list))
    notice_list[max_index].find_element_by_class_name('close_notice').click()
    z_index_list.pop(max_index)
    notice_list.pop(max_index)
    driver.execute_script("window.scrollTo(0, 0)")


# 강의 개수 세기
count_lecture = len(driver.find_elements_by_xpath('//*[@id="page-content"]/div/div[1]/div[2]/ul/li'))

for i in range(1, count_lecture+1):
    main_page = driver.find_element_by_xpath('//*[@id="page-content"]/div/div[1]/div[2]/ul')
    main_page.find_element_by_xpath(f'./li[{i}]/div/a/div').click()
    time.sleep(1)
    url = "https://plato.pusan.ac.kr/report/ubcompletion/user_progress_a.php?id="+str(driver.current_url[-6:])
    driver.execute_script(f'window.open("{url}");')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(0.5)
    main_table = driver.find_element_by_xpath('//*[@id="ubcompletion-progress-wrapper"]/div[2]/table/tbody')
    tr_list = main_table.find_elements_by_tag_name('tr')
    lecture_list = []
    for lec in tr_list:
        td_list = lec.find_elements_by_tag_name('td')
        if len(td_list) == 4:
            if td_list[3].text == "X":
                lecture_list.append(td_list[0].text)
        else:
            if td_list[4].text == "X":
                lecture_list.append(td_list[1].text)


    time.sleep(0.5)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(0.5)

    if len(lecture_list) == 0:
        driver.get('https://plato.pusan.ac.kr/')
        time.sleep(1)
        continue

    now_index = 0
    # li_list는 1주차부터 16주차까지 block들이 담겨있는 list
    li_list = driver.find_element_by_xpath('//*[@id="course-all-sections"]/div/ul').find_elements_by_tag_name('li')
    for index, li in enumerate(li_list):
        num = index + 1
        ul_list = li.find_element_by_xpath(f'//*[@id="section-{num}"]/div[3]').find_elements_by_tag_name('ul')
        # "len(ul_list) == 0" 은 그 주차에 아무 강의 자료 없다는 뜻 
        if len(ul_list) == 0:
            continue
        # file 하나하나 탐색
        for file in ul_list[0].find_elements_by_tag_name('li'):
            my_text = file.text
            if ((lecture_list[now_index] in my_text) and ("동영상" in my_text)):
                duration = my_text[my_text.find('동영상')+5:my_text.find('동영상')+46]
                from_d = datetime.strptime(duration[:19], "%Y-%m-%d %H:%M:%S")
                until_d = datetime.strptime(duration[22:], "%Y-%m-%d %H:%M:%S")

                # 출석인정기간인 경우
                if (from_d <= time_now) and (time_now <= until_d):
                    print(lecture_list[now_index], "듣는 중...")
                    raw_url = file.find_element_by_tag_name('a').get_attribute('onclick')
                    url = raw_url[raw_url.find("https"):raw_url.find("', '', '")]
                    driver.execute_script(f'window.open("{url}");')
                    driver.switch_to.window(driver.window_handles[1])
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    temp = driver.page_source
                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass
                    driver.find_element_by_xpath('//*[@id="vod_viewer"]').click()

                    while True:
                        left_hour = driver.find_element_by_xpath('//*[@id="my-video"]/div[4]/div[7]/div').text
                        if "-0:00" == left_hour:
                            break
                        time.sleep(60)

                    driver.find_element_by_class_name('vod_close_button').click()
                    time.sleep(2)

                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass

                    driver.switch_to.window(driver.window_handles[0])
                    print(lecture_list[now_index], "완료")
                    time.sleep(0.5)

                now_index += 1

                if len(lecture_list) == now_index:
                    # 이번 주차의 파일 하나 하나 탐색하는 for문을 break
                    break
        if len(lecture_list) == now_index:
            # 다음 주차의 블록으로 넘어가지 않는다는 break
            break                                                                                                                                                               

    driver.get('https://plato.pusan.ac.kr/')
    time.sleep(1)

driver.close()