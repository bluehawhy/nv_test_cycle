from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import sys, os
import re
import chromedriver_autoinstaller


#add internal libary
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from _api import loggas, configus, selena
#from _src._api import loggas, configus, selena

#make logpath
logging= loggas.logger

#loading config data
config_path = 'static\config\config.json'
selenium_path = 'static\config\selenium.json'
message_path = configus.load_config(config_path)['message_path']

def make_excel_data(data,ws_list):
    tc_data ={}
    for row_index in ws_list:
        tc_data[str(row_index)] = str(data[ws_list.index(row_index)].value)
        tc_data['updateDefectList'] = 'true'
    return tc_data





#=================================================================================================

def driver_get_step_id(driver,ExecutionId=None, OrderId=None):
    status = False
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']
    full_url = str(config_data['test_cycle_url']).replace('excution_id',ExecutionId)
    selena.driver_get_to_url(driver,full_url)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"row-column.grid-column.orderId-column")))
    step_id = driver.find_element(By.CLASS_NAME,"row-column.grid-column.orderId-column")
    step_id_all = step_id.get_attribute('innerHTML')
    first_step_id = re.findall('data-stepid="([0-9]*)"',step_id_all)[0]
    logging.info(first_step_id)
    return status, first_step_id


#=================================================================================================
# this is execution field update 
def update_execution_result(driver, ExecutionId, ExecutionStatus):
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']

    #set update_status
    update_status = False
    #value is None
    if ExecutionStatus is None:
        logging.info(f'execution status is none')
        update_status = True
        return update_status

    #call url
    full_url = str(test_cycle_url).replace('excution_id',ExecutionId)
    get_to_status, driver = selena.driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    xpath_current_value = '//*[@id="current-execution-status-dd-schedule-%s"]' %ExecutionId
    find_status, current_value = selena.xpath_element_get_text(driver,xpath_current_value)
    
    #check values
    if find_status is False:
        logging.info(f'fail to current value, so skip the update')
        return update_status
    
    #if already inputted.
    if current_value == ExecutionStatus:
        logging.info('execution result already inputted. - %s' %(current_value))
        loggas.input_message(path = message_path,message = f'execution result already inputted. - {current_value}')
        update_status = True
        return update_status
    
    #start input
    logging.info(f'execution result : current - "{current_value}", new - "{ExecutionStatus}"')
    loggas.input_message(path = message_path,message = f'execution result : current - "{current_value}", new - "{ExecutionStatus}"')
    
    #select combo box
    execution_xpath = '//*[@id="executionStatus-trigger-%s"]' %ExecutionId
    find_status, xpath_element = selena.xpath_element_click(driver,execution_xpath)
    if find_status is False:
        logging.info(f'fail to find {execution_xpath}, so skip the update')
        return update_status
    
    #select execution id
    Execution_xpath_result_id = '//*[@id="exec_status-schedule-%s"]/ul/li[@data-str="%s"]' %(ExecutionId, ExecutionStatus)
    find_status, xpath_element = selena.xpath_element_click(driver,Execution_xpath_result_id)
    if find_status is False:
        logging.info(f'fail to find {Execution_xpath_result_id}, so skip the update')
        return update_status
    time.sleep(0.5)

    #done - return update_status
    update_status = True
    return update_status

def update_execution_comment(driver, ExecutionId, Comment):
    #set update_status
    update_status = False
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']
    
    #value is None
    if Comment == "None":
        logging.info(f'Comment is none, skip the update')
        update_status = True
        return update_status
    
    #call url
    full_url = str(test_cycle_url).replace('excution_id',ExecutionId)
    get_to_status, driver = selena.driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    time.sleep(0.5)
    xpath_comment = '//*[@id="comment-val"]'
    find_status, xpath_comment_value = selena.xpath_element_get_text(driver,xpath_comment)
    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status
    
    #if already inputted.
    if xpath_comment_value == Comment:
        #logging.info('execution comment already inputted.')
        loggas.input_message(path = message_path,message = f'execution comment already inputted. -"{Comment}"')
        update_status = True
        return update_status
    
    #start input
    logging.info('start add execution comment.')
    loggas.input_message(path = message_path,message = 'start add execution comment - %s' %Comment)
    time.sleep(0.5)
    find_status, xpath_element = selena.xpath_element_click(driver,xpath_comment)
    if find_status is False:
        logging.info(f'fail to find {xpath_comment}, so skip the update')
        return update_status
    
    
    ##clear textarea and input new one
    xpath_comment_area ='//*[@id="schedule-comment-area"]'    
    clear_status, xpath_comment_value = selena.xpath_element_clear(driver,xpath_comment_area)
    if clear_status is False:
        logging.info(f'fail to clear {xpath_comment_area}, so skip the update')
        return update_status
    
    text_feild_xpath_comment_area =driver.find_element("xpath",xpath_comment_area)
    text_feild_xpath_comment_area.send_keys(Comment)
    time.sleep(0.5)

    #close comment 
    xpath_comment_enter = '//*[@id="comment-counter"]'
    find_status, xpath_element = selena.xpath_element_click(driver,xpath_comment_enter)
    if find_status is False:
        logging.info(f'fail to find {xpath_comment_enter}, so skip the update')
        return update_status
    time.sleep(0.5)

def update_execution_defect(driver, ExecutionId ,execution_defect):
    #set update_status
    update_status = False
    #find element
    xpath_defects = '//*[@id="zephyrJEdefectskey-schedule-%s-multi-select"]/div[2]' %ExecutionId
    find_status, xpath_defects_value = selena.xpath_element_get_text(driver,xpath_defects)
    
    xpath_defects_value =driver.find_element("xpath",xpath_defects)
    defect_outerHTML = xpath_defects_value.get_attribute('outerHTML')
    if execution_defect in defect_outerHTML:
        logging.info('%s already added in test execution' %execution_defect)
    else: 
        logging.info('start to add %s into test execution' %execution_defect)
        xpath_defects_text_area = '//*[@id="zephyrJEdefectskey-schedule-%s-textarea"]' %ExecutionId
        driver.find_element("xpath",xpath_defects_text_area).click()
        time.sleep(0.5)
        driver.find_element("xpath",xpath_defects_text_area).send_keys(execution_defect)
        driver.find_element("xpath",'//*[@id="zexecute"]/fieldset/div[1]/div[2]/div[2]/div/div/label').click()
        time.sleep(0.5)
    return update_status
#=================================================================================================

#=================================================================================================
# this is step field update 
def update_step_result(driver, ExecutionId, OrderId,Step_Result):
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']
    #set update_status
    update_status = False

    #set id of test result
    if Step_Result in config_data['test_resut_sel'].keys():
        step_resut_number = config_data['test_resut_sel'][Step_Result]
    else:
        logging.info('there is no list in test result list, please check your reulst - %s' %Step_Result)
        step_resut_number = '6'
    logging.info('test_resut_number is %s ExecutionStatus is %s' %(step_resut_number,Step_Result))
    
    #call url
    full_url = str(test_cycle_url).replace('excution_id',ExecutionId)
    get_to_status, driver = selena.driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status

    #get current value
    step_xpath_result = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div' %OrderId
    find_status, xpath_step_result_value = selena.xpath_element_get_text(driver,step_xpath_result)

    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status

    #if already inputted.
    if xpath_step_result_value == Step_Result:
        logging.info(f'step result already inputted. - {xpath_step_result_value}')
        loggas.input_message(path = message_path,message = f'step result already inputted. - {xpath_step_result_value}')
        update_status = True
        return update_status


    
    #start input
    xpath_step_result_trigger_dropDown = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/span[3]' %OrderId
    find_status, xpath_element = selena.xpath_element_click(driver,xpath_step_result_trigger_dropDown)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    

    #check combo box shown
    step_xpath_step_result_combo = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/div/ul' %OrderId
    find_status, xpath_element = xpath_element_find(driver,xpath_step_result_trigger_dropDown)
    if find_status is False:
        find_status, xpath_element = selena.xpath_element_click(driver,xpath_step_result_trigger_dropDown)

    step_xpath_result_id = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/div/ul/li[%s]' %(OrderId, step_resut_number)
    find_status, xpath_element = selena.xpath_element_click(driver,step_xpath_result_id)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    
    time.sleep(0.5)
    update_status = True
    return update_status

def update_step_comment(driver, ExecutionId, OrderId, step_comment):
    #call tc url
    config_data =configus.load_config(config_path)
    test_cycle_url = config_data['test_cycle_url']

    #set update_status
    update_status = False

    #value is None
    if step_comment == "None":
        logging.info(f'step_comment is none, skip the update')
        update_status = True
        return update_status
    
    #call url
    full_url = str(test_cycle_url).replace('excution_id',ExecutionId)
    get_to_status, driver = selena.driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    step_xpath_comment = '//*[@id="unfreezedGridBody"]/div[7]/div[%s]/div' %OrderId
    find_status, xpath_step_comment_value = selena.xpath_element_get_text(driver,step_xpath_comment)

    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status

    #if already inputted.
    if xpath_step_comment_value == step_comment:
        logging.info('step comment already inputted. - "%s"' %(xpath_step_comment_value))
        loggas.input_message(path = message_path,message = 'step comment already inputted. - "%s"' %(xpath_step_comment_value))
        update_status = True
        return update_status
    
    #start input
    #select text feild
    find_status, xpath_element = selena.xpath_element_click(driver,step_xpath_comment)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    time.sleep(0.5)

    ##clear textarea and input new one
    xpath_step_comment_area ='//*[@id="unfreezedGridBody"]/div[7]/div[%s]' %OrderId
    clear_status, xpath_comment_value = selena.xpath_element_clear(driver,xpath_step_comment_area)
    if clear_status is False:
        logging.info(f'fail to clear {xpath_step_comment_area}, so skip the update')
        return update_status

    time.sleep(0.5)
    text_feild_xpath_step_comment_area =driver.find_element("xpath",xpath_step_comment_area)
    try:
        text_feild_xpath_step_comment_area.send_keys(step_comment)
    except:
        update_status = False
        return update_status

    time.sleep(0.5)

    #close comment 
    time.sleep(0.5)
    find_status, xpath_element = selena.xpath_element_click(driver,'//*[@id="unfreezedGridHeader"]/div[2]/div/div')
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    time.sleep(0.5)
    return 0

def update_step_defect(driver,OrderId,step_defects):
    return 0
#=================================================================================================


#execution defect 처리
def serperate_defects(ExecutionDefects):
    split_1 = '|'
    split_2 = ','
    execution_defects = []
    step_defects = []
    if ExecutionDefects =="None":
        return execution_defects, step_defects
    else:
        if split_1 in ExecutionDefects:
            temp_execution_defects = ExecutionDefects.split(split_1)[0].split(split_2)
            for temp_execution_defect in temp_execution_defects:
                execution_defect = temp_execution_defect.strip()
                execution_defects.append(execution_defect)
            temp_step_defects = ExecutionDefects.split(split_1)[1].split(split_2)
            for temp_step_defect in temp_step_defects:
                step_defect = temp_step_defect.strip()
                step_defects.append(step_defect)
        else:
            temp_step_defects = ExecutionDefects.split(split_1)[0].split(split_2)
            for temp_step_defect in temp_step_defects:
                step_defect = temp_step_defect.strip()
                step_defects.append(step_defect)
    return execution_defects, step_defects

def input_all_execution_data(driver, execution_data):
    logging.info('%s' %(str(execution_data)))
    ExecutionId = execution_data['ExecutionId']
    ExecutionStatus = execution_data['ExecutionStatus']
    Comment = execution_data['Comment']
    ExecutionDefects = execution_data['ExecutionDefects']
    OrderId = execution_data['OrderId']
    Step_Result = execution_data['Step Result']
    Comments = execution_data['Comments']
    OrderId = execution_data['OrderId']
    
    logging.info('update defect list - %s' %str(serperate_defects(ExecutionDefects)))
    loggas.input_message(path = message_path,message ='update defect list - %s' %str(serperate_defects(ExecutionDefects)))
    execution_defects, step_defects = serperate_defects(ExecutionDefects)

    status_update_execution_result = False
    status_update_execution_comment = False
    status_update_step_result = False
    status_update_step_comment = False

    if OrderId == "1":
        logging.info(f'call update_execution_result')
        status_update_execution_result = update_execution_result(driver, ExecutionId, ExecutionStatus)
        logging.info(f'call update_execution_comment')
        status_update_execution_comment = update_execution_comment(driver, ExecutionId,Comment)
        logging.info(f'call update_step_result')
        status_update_step_result = update_step_result(driver,ExecutionId, OrderId,Step_Result)
        logging.info(f'call update_step_comment')
        status_update_step_comment = True #update_step_comment(driver,ExecutionId, OrderId,Comments)
        #for execution_defect in execution_defects:
        #    update_execution_defect(driver, ExecutionId ,execution_defect)
        
    else:
        status_update_execution_result = None
        status_update_execution_comment = None
        logging.info(f'call update_step_result')
        status_update_step_result = update_step_result(driver,ExecutionId, OrderId,Step_Result)
        logging.info(f'call update_step_comment')
        status_update_step_comment = True #update_step_comment(driver,ExecutionId, OrderId,Comments)
        #for step_defect in step_defects:
        #    update_step_defect(driver,OrderId,step_defect)
    return status_update_execution_result, status_update_execution_comment, status_update_step_result, status_update_step_comment

#=================================================================================================

