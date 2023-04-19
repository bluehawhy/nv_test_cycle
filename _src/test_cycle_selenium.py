from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import chromedriver_autoinstaller


#add internal libary
from _src._api import logger, excel, config, logging_message

#make logpath
logging= logger.logger

#loading config data
config_path = 'static\config\config.json'
config_data =config.load_config(config_path)
test_cycle_url = config_data['test_cycle_url']
jira_login_url = config_data['jira_login_url']
message_path = config_data['message_path']
jira_id = config_data['id']
jira_password = config_data['password']

def make_excel_data(data,ws_list):
    tc_data ={}
    for row_index in ws_list:
        tc_data[str(row_index)] = str(data[ws_list.index(row_index)].value)
        tc_data['updateDefectList'] = 'true'
    return tc_data

#=================================================================================================
# set up driver. 
def moveToNextTestStep(driver):
    #spand step list to 50
    #this is running when test step is over 50 (not need currently)
    time.sleep(0.5)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, 'pagination-dropdown-button')))
    driver.find_element("xpath",'//*[@id="pagination-dropdown-button"]').click()
    time.sleep(0.5)
    return 0

def call_drivier():
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920x1080')
    #options.add_argument('disable-gpu')
    options.add_argument('lang=ko_KR')
    options.add_argument('headless') # HeadlessChrome 사용시 브라우저를 켜지않고 크롤링할 수 있게 해줌
    #options.add_argument('User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36')
    # 헤더에 headless chrome 임을 나타내는 내용을 진짜 컴퓨터처럼 바꿔줌.
    try:
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe',options=options)  
    except:
        logging.info('install chromedriver')
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe',options=options)
    return driver

def login(driver):
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

def xpath_element_return(driver,xpath):
    status = False
    try:
        xpath_element = driver.find_element("xpath",xpath)
        status = True
    except:
        logging.info(f'not found element')
        xpath_element = None
    return status, xpath_element

def xpath_element_get_text(driver,xpath):
    status = False
    try:
        xpath_element = driver.find_element("xpath",xpath)
        xpath_element_txt = xpath_element.text
        status = True
    except:
        logging.info(f'not found element')
        xpath_element_txt = None
    return status, xpath_element_txt

def xpath_element_click(driver,xpath):
    status = False
    try:
        xpath_element = driver.find_element("xpath",xpath)
        xpath_element.click()
        status = True
    except:
        logging.info(f'not found element')
        xpath_element = None
    return status, xpath_element

def driver_get_to_url(driver,url):
    get_to_status = False
    get_url = driver.current_url
    #check url and skip and get to url.
    if url == get_url:
        logging.info('current url is same with previous one so driver doesn\'t get to %s' %(get_url))
        get_to_status = True
    else:
        logging.info('search for %s' %(url))
        logging_message.input_message(path = message_path,message = 'search for %s' %(url))
        try:
            x_path = '//*[@id="pagination-dropdown-button"]/span'
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.visibility_of_element_located((By.XPATH,x_path)))
            find_status, xpath_element = xpath_element_return(driver,x_path)
            if find_status is True:
                get_to_status = True
            else:
                get_to_status = False
        except:
            get_to_status = False
    return get_to_status, driver

#=================================================================================================

#=================================================================================================
# this is execution field update 
def update_execution_result(driver, ExecutionId, ExecutionStatus):
    #set update_status
    update_status = False
    #value is None
    if ExecutionStatus is None:
        logging.info(f'execution status is none')
        update_status = True
        return update_status

    #call url
    full_url = test_cycle_url.replace('excution_id',ExecutionId)
    get_to_status, driver = driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    xpath_current_value = '//*[@id="current-execution-status-dd-schedule-%s"]' %ExecutionId
    find_status, current_value = xpath_element_get_text(driver,xpath_current_value)
    
    #check values
    if find_status is False:
        logging.info(f'fail to current value, so skip the update')
        return update_status
    
    #if already inputted.
    if current_value == ExecutionStatus:
        logging.info('execution result already inputted. - %s' %(current_value))
        logging_message.input_message(path = message_path,message = f'execution result already inputted. - {current_value}')
        update_status = True
        return update_status
    
    #start input
    logging.info(f'execution result : current - "{current_value}", new - "{ExecutionStatus}"')
    logging_message.input_message(path = message_path,message = f'execution result : current - "{current_value}", new - "{ExecutionStatus}"')
    
    #select combo box
    execution_xpath = '//*[@id="executionStatus-trigger-%s"]' %ExecutionId
    find_status, xpath_element = xpath_element_return(driver,execution_xpath)
    if find_status is False:
        logging.info(f'fail to find {execution_xpath}, so skip the update')
        return update_status
    xpath_element.click()
    time.sleep(0.5)

    #select execution id
    Execution_xpath_result_id = '//*[@id="exec_status-schedule-%s"]/ul/li[@data-str="%s"]' %(ExecutionId, ExecutionStatus)
    find_status, xpath_element = xpath_element_click(driver,Execution_xpath_result_id)
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
    
    #value is None
    if Comment == "None":
        logging.info(f'Comment is none, skip the update')
        update_status = True
        return update_status
    
    #call url
    full_url = test_cycle_url.replace('excution_id',ExecutionId)
    get_to_status, driver = driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    xpath_comment = '//*[@id="comment-val"]'
    find_status, xpath_comment_value = xpath_element_get_text(driver,xpath_comment)
    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status
    
    #if already inputted.
    if xpath_comment_value == Comment:
        #logging.info('execution comment already inputted.')
        logging_message.input_message(path = message_path,message = f'execution comment already inputted. -"{Comment}"')
        update_status = True
        return update_status
    
    #start input
    logging.info('start add execution comment.')
    logging_message.input_message(path = message_path,message = 'start add execution comment - %s' %Comment)
    driver.find_element("xpath",xpath_comment).click()
    time.sleep(0.5)
    xpath_comment_area ='//*[@id="schedule-comment-area"]'
    text_feild_xpath_comment_area =driver.find_element("xpath",xpath_comment_area)
    text_feild_xpath_comment_area.clear()
    text_feild_xpath_comment_area.send_keys(Comment)
    time.sleep(0.5)
    driver.find_element("xpath",'//*[@id="comment-counter"]').click()

def update_execution_defect(driver, ExecutionId ,execution_defect):
    #현재는 값 추가만 적용, 차후 삭제 비교도 진행 해야함.
    xpath_defects = '//*[@id="zephyrJEdefectskey-schedule-%s-multi-select"]/div[2]' %ExecutionId
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
    return 0
#=================================================================================================

#=================================================================================================
# this is step field update 
def update_step_result(driver, ExecutionId, OrderId,Step_Result):
    #set update_status
    update_status = False

    #call url
    full_url = test_cycle_url.replace('excution_id',ExecutionId)
    get_to_status, driver = driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status

    #get current value
    step_xpath_result = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div' %OrderId
    find_status, xpath_step_result_value = xpath_element_get_text(driver,step_xpath_result)

    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status

    #if already inputted.
    if xpath_step_result_value == Step_Result:
        logging.info(f'step result already inputted. - {xpath_step_result_value}')
        logging_message.input_message(path = message_path,message = f'step result already inputted. - {xpath_step_result_value}')
        update_status = True
        return update_status
        
    #start input
    time.sleep(0.5)
    step_xpath_result = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/span[3]' %OrderId
    find_status, xpath_element = xpath_element_click(driver,step_xpath_result)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    
    
    #set id of test result
    if Step_Result in config_data['test_resut_sel'].keys():
        step_resut_number = config_data['test_resut_sel'][Step_Result]
    else:
        logging.info('there is no list in test result list, please check your reulst - %s' %Step_Result)
        step_resut_number = '6'
    logging.info('test_resut_number is %s ExecutionStatus is %s' %(step_resut_number,Step_Result))
    
    step_xpath_result_id = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/div/ul/li[%s]' %(OrderId, step_resut_number)
    find_status, xpath_element = xpath_element_click(driver,step_xpath_result_id)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    
    time.sleep(0.5)
    update_status = True
    return update_status

def update_step_comment(driver, ExecutionId, OrderId, step_comment):
    #set update_status
    update_status = False

    #value is None
    if step_comment == "None":
        logging.info(f'step_comment is none, skip the update')
        update_status = True
        return update_status
    
    #call url
    full_url = test_cycle_url.replace('excution_id',ExecutionId)
    get_to_status, driver = driver_get_to_url(driver,full_url)
    if get_to_status is False:
        logging.info(f'fail to get current url, so skip the update')
        update_status = False
        return update_status
    
    #get current value
    step_xpath_comment = '//*[@id="unfreezedGridBody"]/div[7]/div[%s]/div' %OrderId
    find_status, xpath_step_comment_value = xpath_element_get_text(driver,step_xpath_comment)

    if find_status is False:
        logging.info(f'fail to get current value, so skip the update')
        update_status = False
        return update_status

    #if already inputted.
    if xpath_step_comment_value == step_comment:
        logging.info('step comment already inputted. - "%s"' %(xpath_step_comment_value))
        logging_message.input_message(path = message_path,message = 'step comment already inputted. - "%s"' %(xpath_step_comment_value))
        update_status = True
        return update_status
    
    #start input
    #select text feild
    find_status, xpath_element = xpath_element_click(driver,step_xpath_comment)
    if find_status is False:
        logging.info(f'fail to click current value, so skip the update')
        update_status = False
        return update_status
    time.sleep(0.5)
    #clear textarea 
    step_xpath_comment_feild = driver.find_elements("xpath",'//*[@id="editMode"]/div/textarea')[int(OrderId)-1]
    step_xpath_comment_feild.clear()
    
    #and send key.
    logging.info('start input step comment - %s' %(str(step_comment)))
    logging_message.input_message(path = message_path,message = 'start input step comment - %s' %(str(step_comment)))
    step_xpath_comment_feild.send_keys(step_comment)
    find_status, xpath_element = xpath_element_click(driver,'//*[@id="unfreezedGridHeader"]/div[2]/div/div')
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
    logging_message.input_message(path = message_path,message ='update defect list - %s' %str(serperate_defects(ExecutionDefects)))
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
        status_update_step_comment = update_step_comment(driver,ExecutionId, OrderId,Comments)
        #for execution_defect in execution_defects:
        #    update_execution_defect(driver, ExecutionId ,execution_defect)
        
    else:
        status_update_execution_result = True
        status_update_execution_comment = True
        logging.info(f'call update_step_result')
        status_update_step_result = update_step_result(driver,ExecutionId, OrderId,Step_Result)
        logging.info(f'call update_step_comment')
        status_update_step_comment = update_step_comment(driver,ExecutionId, OrderId,Comments)
        #for step_defect in step_defects:
        #    update_step_defect(driver,OrderId,step_defect)
    return status_update_execution_result, status_update_execution_comment, status_update_step_result, status_update_step_comment

#=================================================================================================
def update_test_cycle(file):
    # loading excel data
    logging.info('start importing test cycle - %s' %file)
    logging_message.input_message(path = message_path,message = f'start importing test cycle - {file}')
    wb = excel.Workbook(file,read_only=False,data_only=True)

    #set worksheet
    worksheet = config_data['worksheet']
    logging.info('search for %s in %s' %(worksheet,str(wb.get_sheet_list())))
    logging_message.input_message(path = message_path,message = f'search for {worksheet} in {str(wb.get_sheet_list())}')
    if worksheet not in wb.get_sheet_list():
        logging.info('there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        worksheet = wb.get_sheet_list()[0]
        config_data['worksheet'] = worksheet
        config.save_config(config_data,config_path)
    else:
        logging.info('there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
    
    #add update_status
    tc_ws = wb.get_worksheet(worksheet)
    tc_row_index = wb.get_first_row(worksheet)
    if 'update_status' not in tc_row_index:
        logging.info('need to add update_status')
        wb.change_cell_data(tc_ws, len(tc_row_index)+1, 1, 'update_status')
        wb.save_workbook(file)
        wb.close_workbook()
    else:
        logging.info('already inputted update_status')
        wb.close_workbook()
    
    #check index data
    tc_ws = wb.get_worksheet(worksheet)
    tc_row_index = wb.get_first_row(worksheet)
    index_config = config_data['excel_index']
    def check_file_vaild(index_config, tc_row_index):
        logging.info(f'check row index')
        file_valid = False
        index_config_key = list(index_config.values())
        index_diff = [x for x in index_config_key if x in tc_row_index]
        index_miss = [x for x in index_config_key if x not in tc_row_index]
        file_valid = (len(index_diff) == len(index_config_key))
        return file_valid , index_miss
    file_valid , index_miss = check_file_vaild(index_config, tc_row_index)
    if file_valid is False:
        logging.info(f'some indexs are missing - {str(index_miss)}')
        wb.close_workbook()
        return 0
    #=======================================================================================================
    
    #start selenium
    #set up chromedriver
    driver = call_drivier()
    login(driver)
    #=======================================================================================================

    cnt = 0
    for data in tc_ws.rows:
        cnt += 1
        tc_data = {}
        tc_data = make_excel_data(data,tc_row_index)
        #if first cell is None => break
        ExecutionId = tc_data['ExecutionId']
        StepId = tc_data['StepId'] if 'StepId' in tc_data.keys() else None
        OrderId = tc_data['OrderId'] if 'OrderId' in tc_data.keys() else None
        update_status = tc_data['update_status']
        logging_message.input_message(path = message_path,message = f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
        logging.info(f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
        if ExecutionId in ('None',None):
            break
        elif ExecutionId == 'ExecutionId':
            logging.info(f'this is first low')
        elif update_status == 'True':
            logging.info(f'update status is True')
        else:
            status_update_execution_result, status_update_execution_comment, status_update_step_result, status_update_step_comment = input_all_execution_data(driver, tc_data)
            result_value = f'status_update_execution_result - {status_update_execution_result}, status_update_execution_comment - {status_update_execution_comment}, status_update_step_result - {status_update_step_result}, status_update_step_comment - {status_update_step_comment}'
            total_result =  all((status_update_execution_result, status_update_execution_comment, status_update_step_result, status_update_step_comment))
            logging.info(f'{result_value} - total_result : {total_result}')
            wb.change_cell_data(tc_ws, tc_row_index.index('update_status')+1, cnt, total_result)
    logging_message.input_message(path = message_path,message ='import done and close workbook!')
    logging.info('import done!')
    wb.save_workbook(file)
    logging.info('close workbook!')
    wb.close_workbook()
    logging.info('close driver!')
    driver.close()
    return 0    







