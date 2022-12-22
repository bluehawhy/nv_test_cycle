from lib2to3.pgen2.driver import Driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import sys, time


#add internal libary
from _src._api import logger

#make logpath
logging= logger.logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def start(execution_data,test_cycle_url):
    #set up chromedriver
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920x1080')
    #options.add_argument('disable-gpu')
    options.add_argument('lang=ko_KR')
    #options.add_argument('headless')
    # HeadlessChrome 사용시 브라우저를 켜지않고 크롤링할 수 있게 해줌
    #options.add_argument('User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36')
    # 헤더에 headless chrome 임을 나타내는 내용을 진짜 컴퓨터처럼 바꿔줌.
    try:
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe',options=options)  
    except:
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe',options=options)
    
    logging.info('%s' %(str(execution_data)))
    ExecutionId = execution_data['ExecutionId']
    StepId = execution_data['StepId'] 
    ExecutionStatus = execution_data['ExecutionStatus']
    Comment = execution_data['Comment']
    ExecutionDefects = execution_data['ExecutionDefects']
    OrderId = execution_data['OrderId']
    Step_Result = execution_data['Step Result']
    Comments = execution_data['Comments']
    full_url = test_cycle_url + ExecutionId
    driver.get(full_url)
