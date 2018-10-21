from selenium import webdriver

browser = webdriver.Chrome(executable_path='/home/Rilzob/公共/Articlespider/chromedriver')

browser.get('http://www.innotree.cn/login.html')
print(browser.page_source)

browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('15724428236')
browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('watermirrorsir')

browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').click()
