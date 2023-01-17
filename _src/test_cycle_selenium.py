from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def moveToNextTestStep(driver):
    #spand step list to 50
    #this is running when test step is over 50 (not need currently)
    time.sleep(0.2)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, 'pagination-dropdown-button')))
    driver.find_element("xpath",'//*[@id="pagination-dropdown-button"]').click()
    time.sleep(0.2)
    return 0

def login(driver):
    #start login
    driver.implicitly_wait(10)
    driver.get(jira_login_url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, 'login-form-submit')))
    username=driver.find_element("xpath",'//*[@id="login-form-username"]')
    username.send_keys(jira_id)
    password=driver.find_element("xpath",'//*[@id="login-form-password"]')
    password.send_keys(jira_password)
    time.sleep(0.2)
    driver.find_element("xpath",'//*[@id="login-form-submit"]').click()
    return 0


#=================================================================================================
# this is execution field update 
def update_execution_result(driver, ExecutionId, ExecutionStatus):
    #check execution value
    xpath_current_value = '//*[@id="current-execution-status-dd-schedule-%s"]' %ExecutionId
    current_value =driver.find_element("xpath",xpath_current_value).text
    logging.info('current execution value - "%s", execution result - "%s"' %(current_value,ExecutionStatus))
    #logging_message.input_message(path = message_path,message = 'current execution value - "%s", execution result - "%s"' %(current_value,ExecutionStatus))
    if current_value == ExecutionStatus:
        logging.info('execution result already inputted. - %s' %(current_value))
        logging_message.input_message(path = message_path,message = 'execution result already inputted. - %s' %(current_value))
        return 0
    else:
        if ExecutionStatus == None:
            return 0
        logging.info('execution-status(%s) is diff with result(%s).' %(current_value,ExecutionStatus))
        logging_message.input_message(path = message_path,message = 'execution-status(%s) is diff with result(%s).' %(current_value,ExecutionStatus))
        #input execution
        wait = WebDriverWait(driver, 20)
        execution_xpath = '//*[@id="executionStatus-trigger-%s"]' %ExecutionId
        element = wait.until(EC.element_to_be_clickable((By.XPATH,execution_xpath)))
        driver.find_element("xpath",execution_xpath).click()
        time.sleep(0.2)
        Execution_xpath_result_id = '//*[@id="exec_status-schedule-%s"]/ul/li[@data-str="%s"]' %(ExecutionId, ExecutionStatus)
        logging.info(Execution_xpath_result_id)
        driver.find_element("xpath",Execution_xpath_result_id).click()
        time.sleep(0.2)
        return 0

def update_execution_comment(driver, ExecutionId ,Comment):
    if Comment == "None":
        Comment = ""
    #input comment value
    wait = WebDriverWait(driver, 20)
    xpath_comment = '//*[@id="comment-val"]'
    xpath_comment_value =driver.find_element("xpath",xpath_comment).text
    logging.info('execution current value - "%s", execution comment - "%s"' %(xpath_comment_value,Comment))
    logging_message.input_message(path = message_path,message = 'execution current value - "%s", execution comment - "%s"' %(xpath_comment_value,Comment))
    if xpath_comment_value == Comment:
        logging.info('execution comment already inputted.')
        logging_message.input_message(path = message_path,message = 'execution comment already inputted.')
        return 0
    else:
        logging.info('start add execution comment.')
        logging_message.input_message(path = message_path,message = 'start add execution comment - %s' %Comment)
        element = wait.until(EC.element_to_be_clickable((By.XPATH,xpath_comment)))
        driver.find_element("xpath",xpath_comment).click()
        time.sleep(0.2)
        xpath_comment_area ='//*[@id="schedule-comment-area"]'
        text_feild_xpath_comment_area =driver.find_element("xpath",xpath_comment_area)
        text_feild_xpath_comment_area.clear()
        if Comment == "":
            logging.info('execution comment is None so clear text')
            logging_message.input_message(path = message_path,message = 'execution comment is None so clear text')
            driver.find_element("xpath",'//*[@id="comment-counter"]').click()
            return 0
        text_feild_xpath_comment_area.send_keys(Comment)
        time.sleep(0.2)
        driver.find_element("xpath",'//*[@id="comment-counter"]').click()
        return 0


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
        time.sleep(0.2)
        driver.find_element("xpath",xpath_defects_text_area).send_keys(execution_defect)
        driver.find_element("xpath",'//*[@id="zexecute"]/fieldset/div[1]/div[2]/div[2]/div/div/label').click()
        time.sleep(0.2)
    return 0
#=================================================================================================


#=================================================================================================
# this is step field update 
def update_step_result(driver,OrderId,Step_Result):
    #check step value
    step_xpath_result = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div' %OrderId
    wait = WebDriverWait(driver, 20)
    time.sleep(0.2)
    element = wait.until(EC.element_to_be_clickable((By.XPATH,step_xpath_result)))
    current_value =driver.find_element("xpath",step_xpath_result).text
    logging.info('current step result is %s' %current_value)
    if current_value == Step_Result:
        logging.info('Step Result already inputted. - %s' %(current_value))
        logging_message.input_message(path = message_path,message = 'Step Result already inputted. - %s' %(current_value))
        return 0
    else: 
        step_xpath_result = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/span[3]' %OrderId
        driver.find_element("xpath",step_xpath_result).click()
        time.sleep(0.2)
        #set id of test result
        if Step_Result in config_data['test_resut_sel'].keys():
            step_resut_number = config_data['test_resut_sel'][Step_Result]
        else:
            logging.info('there is no list in test result list, please check your reulst - %s' %Step_Result)
            step_resut_number = '6'
        logging.info('test_resut_number is %s ExecutionStatus is %s' %(step_resut_number,Step_Result))
        step_xpath_result_id = '//*[@id="unfreezedGridBody"]/div[6]/div[%s]/div/div/div/ul/li[%s]' %(OrderId, step_resut_number)
        logging.info(step_xpath_result_id)
        driver.find_element("xpath",step_xpath_result_id).click()
        time.sleep(0.2)
        return 0

def update_step_comment(driver,OrderId,step_comment):
    #modify step comment 
    if step_comment == "None":
        step_comment = ""
    #read comment in test cylce
    step_xpath_comment = '//*[@id="unfreezedGridBody"]/div[7]/div[%s]/div' %OrderId
    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_clickable((By.XPATH,step_xpath_comment)))
    current_value =driver.find_element("xpath",step_xpath_comment).text
    logging.info('current step value - "%s", step comment - "%s"' %(current_value,step_comment))
    logging_message.input_message(path = message_path,message = 'current step value - "%s", step comment - "%s"' %(current_value,step_comment))
    if current_value == step_comment:
        logging.info('step comment already inputted. - "%s"' %(current_value))
        logging_message.input_message(path = message_path,message = 'step comment already inputted. - "%s"' %(current_value))
        return 0
    else:
        #select text feild
        wait.until(EC.element_to_be_clickable((By.XPATH,step_xpath_comment)))
        driver.find_element("xpath",step_xpath_comment).click()
        time.sleep(0.2)
        #clear textarea and send key.
        step_xpath_comment_feild = driver.find_elements("xpath",'//*[@id="editMode"]/div/textarea')[int(OrderId)-1]
        step_xpath_comment_feild.clear()
        if step_comment == "":
            logging.info('step comment is None so clear text')
            logging_message.input_message(path = message_path,message = 'step comment is None so clear text')
            driver.find_element("xpath",'//*[@id="unfreezedGridHeader"]/div[2]/div/div').click()
            return 0
        logging.info('start input step comment - %s' %(str(step_comment)))
        logging_message.input_message(path = message_path,message = 'start input step comment - %s' %(str(step_comment)))
        step_xpath_comment_feild.send_keys(step_comment)
        driver.find_element("xpath",'//*[@id="unfreezedGridHeader"]/div[2]/div/div').click()        
        time.sleep(0.2)
        return 0

def update_step_defect(driver,OrderId,step_defects):
    return 0
#=================================================================================================


def input_execution(driver, execution_data):
    logging.info('%s' %(str(execution_data)))
    ExecutionId = execution_data['ExecutionId']
    ExecutionStatus = execution_data['ExecutionStatus']
    Comment = execution_data['Comment']
    ExecutionDefects = execution_data['ExecutionDefects']
    OrderId = execution_data['OrderId']
    Step_Result = execution_data['Step Result']
    Comments = execution_data['Comments']
    OrderId = execution_data['OrderId']

    full_url = test_cycle_url.replace('excution_id',ExecutionId)
    get_url = driver.current_url
    
    #check url and skip and get to url.
    if full_url == get_url:
        logging.info('current url is %s' %(get_url))
        logging.info('current url is same with previous one so driver doesn\'t get to %s' %(get_url))
    else:
        logging.info('search for %s' %(full_url))
        logging_message.input_message(path = message_path,message = 'search for %s' %(full_url))
        driver.get(full_url)
        time.sleep(0.2)
    
    
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
    logging.info('update defect list - %s' %str(serperate_defects(ExecutionDefects)))
    logging_message.input_message(path = message_path,message ='update defect list - %s' %str(serperate_defects(ExecutionDefects)))
    execution_defects = serperate_defects(ExecutionDefects)[0]
    step_defects = serperate_defects(ExecutionDefects)[1]

    if OrderId == "1":
        update_execution_result(driver, ExecutionId, ExecutionStatus)
        update_execution_comment(driver, ExecutionId,Comment)
        for execution_defect in execution_defects:
            update_execution_defect(driver, ExecutionId ,execution_defect)
        update_step_result(driver,OrderId,Step_Result)
        try:
            update_step_comment(driver,OrderId,Comments)
        except:
            logging.info('update comment is fail')
            logging_message.input_message(path = message_path,message = 'update comment is fail')
        for step_defect in step_defects:
            update_step_defect(driver,OrderId,step_defect)
    else:
        update_step_result(driver,OrderId,Step_Result)
        try:
            update_step_comment(driver,OrderId,Comments)
        except:
            logging.info('update comment is fail')
            logging_message.input_message(path = message_path,message = 'update comment is fail')
        for step_defect in step_defects:
            update_step_defect(driver,OrderId,step_defect)

def update_test_cycle(file):
    # loading excel data
    logging.info('start importing test cycle - %s' %file)
    logging_message.input_message(path = message_path,message = 'start importing test cycle - %s' %file)
    wb = excel.Workbook(file,read_only=True,data_only=True)
    logging.info(wb.get_sheet_list())
    worksheet = config_data['worksheet']
    logging.info('search for %s in %s' %(worksheet,str(wb.get_sheet_list())))
    logging_message.input_message(path = message_path,message = 'search for %s in %s' %(worksheet,str(wb.get_sheet_list())))
    if worksheet not in wb.get_sheet_list():
        logging.info('there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is no %s in %s so use first sheet' %(worksheet,str(wb.get_sheet_list())))
        worksheet = wb.get_sheet_list()[0]
        config_data['worksheet'] = worksheet
        config.save_config(config_data,config_path)
    else:
        logging.info('there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
        logging_message.input_message(path = message_path,message = 'there is %s in %s so use the sheet' %(worksheet,str(wb.get_sheet_list())))
    tc_ws = wb.get_worksheet(worksheet)
    tc_row_index = wb.get_first_row(worksheet)
    input_items_tc = config_data['input_items_for_test_cycle']
    logging.info('check row index - %s' %str(tc_row_index))
    logging.info('this is input items for test cycle %s' %input_items_tc.keys())
    #=======================================================================================================
    
    #start selenium
    #set up chromedriver
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
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe',options=options)
    
    driver.implicitly_wait(10) #Implicitly wait for 10 sec
    logging.info('start login')
    login(driver)
    logging.info('login done!')
    #=======================================================================================================

    for data in tc_ws.rows:
        tc_data = {}
        tc_data = make_excel_data(data,tc_row_index)
        #if first cell is None => break
        ExecutionId = tc_data['ExecutionId']
        StepId = tc_data['StepId'] if 'StepId' in tc_data.keys() else None
        OrderId = tc_data['OrderId'] if 'OrderId' in tc_data.keys() else None
        if ExecutionId == 'ExecutionId':
            continue
        if ExecutionId in ('None',None):
            break
        else:
            logging_message.input_message(path = message_path,message = '============ start ExecutionId %s - StepId %s - OrderId %s ============' %(ExecutionId,StepId,OrderId))
            logging.info('============ start ExecutionId %s - StepId %s - OrderId %s ============' %(ExecutionId,StepId,OrderId))
            input_execution(driver, tc_data)
    logging_message.input_message(path = message_path,message ='import done and close workbook!')
    logging.info('import done!')
    logging.info('close workbook!')
    wb.close_workbook()
    logging.info('close driver!')
    driver.close()
    return 0    







