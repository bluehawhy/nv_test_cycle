from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import sys, os
import re


#add internal libary
refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import loggas, configus
if refer_api == "local":
    from _src._api import loggas, configus


#make logpath
logging= loggas.logger

#loading config data
config_path = 'static\config\config.json'
selenium_path = 'static\config\selenium.json'
message_path = configus.load_config(config_path)['message_path']

#=================================================================================================
#=================================================================================================
#=================================================================================================
def make_excel_data(data,ws_list):
    tc_data ={}
    for row_index in ws_list:
        tc_data[str(row_index)] = str(data[ws_list.index(row_index)].value)
        tc_data['updateDefectList'] = 'true'
    return tc_data
#=================================================================================================
#=================================================================================================
#=================================================================================================
    
#=================================================================================================
def login(driver):
    config_data =configus.load_config(config_path)
    jira_login_url = config_data['jira_login_url']
    jira_id = config_data['id']
    jira_password = config_data['password']
    #start login
    logging.info('start login')
    driver.get(jira_login_url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, 'login-form-submit')))
    username=driver.find_element("xpath",'//*[@id="login-form-username"]')
    username.send_keys(jira_id)
    password=driver.find_element("xpath",'//*[@id="login-form-password"]')
    password.send_keys(jira_password)
    time.sleep(0.5)
    driver.find_element("xpath",'//*[@id="login-form-submit"]').click()
    return 0
#=================================================================================================
def xpath_element_find(driver,xpath):
    status = False
    #wait_xpath(driver, xpath)
    try:
        xpath_element = driver.find_element("xpath",xpath)
        status = True
    except:
        logging.info(f'xpath_element_find - not found element')
        xpath_element = None
    return status, xpath_element
#=================================================================================================
def driver_get_to_url(driver,url):
    get_to_status = False
    get_url = driver.current_url
    #check url and skip and get to url.
    if url == get_url:
        logging.info('current url is same with previous one so driver doesn\'t get to %s' %(get_url))
        get_to_status = True
    else:
        logging.info('search for %s' %(url))
        loggas.input_message(path = message_path,message = 'search for %s' %(url))
        try:
            x_path = '//*[@id="pagination-dropdown-button"]/span'
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.visibility_of_element_located((By.XPATH,x_path)))
            find_status, xpath_element = xpath_element_find(driver,x_path)
            if find_status is True:
                get_to_status = True
            else:
                get_to_status = False
        except:
            get_to_status = False
    return get_to_status, driver


#=================================================================================================
def driver_get_step_id(driver,ExecutionId=None, OrderId=None):
    status = False
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']
    full_url = str(config_data['test_cycle_url']).replace('excution_id',ExecutionId)
    driver_get_to_url(driver,full_url)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"row-column.grid-column.orderId-column")))
    time.sleep(1)
    step_id = driver.find_element(By.CLASS_NAME,"row-column.grid-column.orderId-column")
    step_id_all = step_id.get_attribute('innerHTML')
    first_step_id = re.findall('data-stepid="([0-9]*)"',step_id_all)[0]
    logging.info(first_step_id)
    return status, first_step_id
#=================================================================================================
