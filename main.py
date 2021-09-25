from selenium import webdriver
from datetime import datetime, timedelta
import time, os , json

time_now = datetime.now()

options = webdriver.ChromeOptions()
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("-start-maximized")
options.add_argument("--headless")
options.add_argument("--mute-audio")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)
driver.get('https://plato.pusan.ac.kr/')

with open(os.path.join("./", 'secrets.json'), encoding='UTF8') as f:
    secrets = json.loads(f.read())
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

main_page = driver.find_element_by_xpath('//*[@id="page-content"]/div/div[1]/div[2]/ul')
for i in range(1, 100):
    xpath = f'./li[{i}]'
    try:
        main_page.find_element_by_xpath(xpath)
    except:
        count_lecture = i - 1
        break


total_lecture_list = []
card_body = driver.find_element_by_xpath('//*[@id="mCSB_2_container"]/div/div[1]/div[2]')

# for i in range(1, count_lecture+1)
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

    total_lecture_list.append(lecture_list)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.get('https://plato.pusan.ac.kr/')
    time.sleep(1)

for i in range(1, count_lecture+1):
    if len(total_lecture_list[i-1]) == 0:
        continue
    main_page = driver.find_element_by_xpath('//*[@id="page-content"]/div/div[1]/div[2]/ul')
    main_page.find_element_by_xpath(f'./li[{i}]/div/a/div').click()
    weeks_list = driver.find_element_by_xpath('//*[@id="course-all-sections"]/div/ul')
    li_list = weeks_list.find_elements_by_tag_name('li')
    for index, li in enumerate(li_list):
        num = index + 1
        ul_list = li.find_element_by_xpath(f'//*[@id="section-{num}"]/div[3]').find_elements_by_tag_name('ul')
        if len(ul_list) == 0:
            break
        for file in ul_list[0].find_elements_by_tag_name('li'):
            my_text = file.text
            if (total_lecture_list[i-1][0] != 0) and (total_lecture_list[i-1][0] in my_text):
                duration = my_text[my_text.find('동영상')+5:my_text.find('동영상')+46]
                from_d = datetime.strptime(duration[:10], "%Y-%m-%d")
                until_d = datetime.strptime(duration[22:-9], "%Y-%m-%d") + timedelta(days=1)
                if (from_d <= time_now) and (time_now <= until_d):            
                    print(total_lecture_list[i-1][0], "듣는 중...")
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

                    time.sleep(1)
                    driver.find_element_by_class_name('vod_close_button').click()
                    time.sleep(1)  # 동영상 재생 시간

                    try:
                        driver.switch_to.alert.accept()
                    except:
                        pass

                    driver.switch_to.window(driver.window_handles[0])
                    print(total_lecture_list[i-1][0], "듣기 완료")
                if len(total_lecture_list[i-1]) == 1:
                    total_lecture_list[i-1][0] = 0
                else:
                    total_lecture_list[i-1].pop(0)
        if total_lecture_list[i-1][0] == 0:
            break

    driver.get('https://plato.pusan.ac.kr/')
    time.sleep(1)

driver.close()