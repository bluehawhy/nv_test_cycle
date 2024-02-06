#add global libary
import sys, os


#add internal libary
from _src import test_cycle_rest, test_cycle_selenium

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import loggas, excelium, configus, zyra, selena
if refer_api == "local":
    from _src._api import loggas, excelium, configus, zyra, selena

#make logpath
logging= loggas.logger

#loading config data
config_path = 'static\config\config.json'
message_path = configus.load_config(config_path)['message_path']
#======================================================================
#======================================================================
#======================================================================
#========================== function validation =======================
# check excel file
def check_file_vaild(index_config, tc_row_index):
    logging.info(f'check row index')
    file_valid = False
    index_config_key = list(index_config.values())
    index_diff = [x for x in index_config_key if x in tc_row_index]
    index_miss = [x for x in index_config_key if x not in tc_row_index]
    file_valid = (len(index_diff) == len(index_config_key))
    return file_valid , index_miss
#==================== handling test cylce data =======================
def make_excel_data(data,ws_list):
    tc_data ={}
    for row_index in ws_list:
        tc_data[str(row_index)] = str(data[ws_list.index(row_index)].value)
        tc_data['updateDefectList'] = 'true'
    return tc_data
#======================================================================
#======================================================================
#======================================================================
#======================================================================
def get_step_id(driver,tc_data, execution_data):
    #find step_id
    try:
        int(tc_data['ExecutionId'])
    except ValueError:
        return tc_data, execution_data
    else:
        if tc_data['OrderId'] == "None":
            return tc_data, execution_data
        if tc_data['ExecutionId'] in execution_data.keys():
            first_step_id = execution_data[tc_data['ExecutionId']]
            step_id = int(first_step_id)+int(tc_data['OrderId'])-1
            tc_data['StepId'] = step_id
            return tc_data, execution_data
        if tc_data['ExecutionId'] not in execution_data.keys():
            status, first_step_id = test_cycle_selenium.driver_get_step_id(driver,tc_data['ExecutionId'])
            step_id = int(first_step_id)+int(tc_data['OrderId'])-1
            tc_data['StepId'] = step_id
            execution_data[tc_data['ExecutionId']] = first_step_id
            return tc_data, execution_data

#======================= update exection and step ======================
def update_execution_step(rh, execution_data):
    #logging.info(execution_data)
    if execution_data['OrderId'] == "1":
        update_status_execution = test_cycle_rest.update_test_execution(rh,execution_data)
        update_status_step = test_cycle_rest.update_test_step(rh = rh, execution_data = execution_data)
    elif execution_data['OrderId'] == 'None':
        update_status_execution = test_cycle_rest.update_test_execution(rh,execution_data)
        update_status_step = True
    else:
        update_status_execution = True
        update_status_step = test_cycle_rest.update_test_step(rh = rh, execution_data = execution_data)
    return update_status_execution, update_status_step

#=======================================================================================================
#=======================================================================================================
#=======================================================================================================
#=======================================================================================================
#========================== start test cycle ==========================
def update_test_cycle(file):
    config_data =configus.load_config(config_path)
    # loading excel data
    logging.info('start importing test cycle - %s' %file)
    loggas.input_message(path = message_path,message = f'start importing test cycle - {file}')
    wb = excelium.Workbook(file,read_only=False,data_only=True)

    #set worksheet
    worksheet = wb.get_sheet_list()[0]

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
    
    #check excel file is valid (index data)
    tc_ws = wb.get_worksheet(worksheet)
    tc_row_index = wb.get_first_row(worksheet)
    index_config = config_data['excel_index']
    file_valid , index_miss = check_file_vaild(index_config, tc_row_index)
    if file_valid is False:
        logging.info(f'some indexs are missing - {str(index_miss)}')
        wb.close_workbook()
        return 0
    
    #check login status
    session ,session_info, status_login = zyra.initsession(username= config_data['id'], password = config_data['password'] , jira_url = config_data['jira_url'], cert=None)
    if status_login is False:
        return 0
    
    #make REST handler Test cycle
    rh_tc = zyra.Handler_TestCycle(session=session,jira_url=config_data['jira_url'])

    #make selenuim driver
    driver = selena.call_drivier(headless=config_data['headless'])
    test_cycle_selenium.login(driver)


    #=======================================================================================================
    dict_executionid_stepid ={}
    cnt = 0
    for data in tc_ws.rows:
        cnt += 1
        tc_data = {}
        tc_data = make_excel_data(data,tc_row_index)
        tc_data, dict_executionid_stepid = get_step_id(driver=driver,tc_data=tc_data, execution_data = dict_executionid_stepid)
        #if first cell is None => break
        ExecutionId = tc_data['ExecutionId']
        StepId = tc_data['StepId'] if 'StepId' in tc_data.keys() else None
        OrderId = tc_data['OrderId'] if 'OrderId' in tc_data.keys() else None
        update_status = tc_data['update_status']
        total_result = False
        if ExecutionId in ('None',None):
            break
        elif ExecutionId == 'ExecutionId':
            logging.info(f'this is first low')
        elif update_status == 'True':
            loggas.input_message(path = message_path,message = f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
            logging.info(f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
            loggas.input_message(path = message_path,message = f'update status is True')
            logging.info(f'update status is True so pass')
        else:
            loggas.input_message(path = message_path,message = f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
            logging.info(f'============ start ExecutionId {ExecutionId} - StepId {StepId} - OrderId {OrderId} ============')
            logging.info(f'update status is False so start update')
            update_status_execution, update_status_step = update_execution_step(rh_tc, tc_data)
            #make update status
            result_value = f'update_status_execution - {update_status_execution}, update_status_step - {update_status_step}'
            total_result =  all((update_status_execution, update_status_step))
            logging.info(f'{result_value} - total_result : {total_result}')
            loggas.input_message(path = message_path,message = f'{result_value} - total_result : {total_result}')
            wb.change_cell_data(tc_ws, tc_row_index.index('update_status')+1, cnt, total_result)
            #temp_file = os.path.splitext(file)[0]+'_temp'+os.path.splitext(file)[1]
            wb.save_workbook(file)
    loggas.input_message(path = message_path,message ='import done and close workbook!')
    logging.info('import done!')
    wb.save_workbook(file)
    logging.info('close workbook!')
    wb.close_workbook()
    logging.info('close driver!')
    driver.close()
    return 0    
#=======================================================================================================
#=======================================================================================================
#=======================================================================================================
#=======================================================================================================