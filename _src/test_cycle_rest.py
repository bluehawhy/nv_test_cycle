# -*- coding: utf-8 -*-
#!/usr/bin/python


import json
import sys, os


#add internal libary
from _src import test_cycle

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
    from _api import loggas, jason, configus
if refer_api == "local":
    from _src._api import loggas, jason, configus

#make logpath
logging= loggas.logger

#loading config data
config_path = 'static\config\config.json'
config_data =configus.load_config(config_path)
qss_path = config_data['qss_path']
message_path = config_data['message_path']
test_cycle_url = config_data['test_cycle_url']


def update_test_execution(rh = None, execution_data = None):
    status_update_execution = False
    #logging.info('%s' %(str(execution_data)))
    te_playload = {}
    execution_data['ExecutionStatus'] = config_data['execution_result_id'][str(execution_data['ExecutionStatus']).upper()]
    #logging.info('%s' %(str(execution_data)))
    input_items_for_test_exection = config_data['input_items_for_test_exection']
    for input_item_te in input_items_for_test_exection:
        input_data_te = ''
        if execution_data[input_item_te] == "None":
            input_data_te = ''
        else:
            input_data_te = str(execution_data[input_item_te]).replace('\n','\\n')
        input_item_te = str(input_items_for_test_exection[input_item_te]).replace('field_input_value',input_data_te)
        input_item_te = eval(input_item_te)
        te_playload.update(input_item_te['input_playload'])
    
    if 'defectList' in te_playload:
        te_playload['defectList'] = te_playload['defectList'].split(',')

    logging.info('execution id  - %s' %str(execution_data['ExecutionId']))
    logging.info('test execution infomation - %s' %str(te_playload))
    result = rh.updateExecution(execution_data['ExecutionId'],jason.makeplayload(te_playload))
    if result.status_code == 200:
        #logging.info(result.text)
        loggas.input_message(path = message_path,message = 'test execution updated - %s' %str(execution_data['ExecutionId']))
        status_update_execution = True
    else:
        #logging.info(result.text)
        loggas.input_message(path = message_path,message = 'test execution updated error - %s - %s' %(str(execution_data['ExecutionId']),result.text))

    return status_update_execution

def update_test_step(rh = None, execution_data = None):
    status_update_step = False
    ts_playload = {}
    execution_data['Step Result'] = config_data['step_result'][str(execution_data['Step Result']).upper()]
    input_items_for_test_step = config_data['input_items_for_test_step']
    for input_item_ts in input_items_for_test_step:
        try:
            execution_data[input_item_ts]
        except KeyError:
            pass
        else:
            input_data_ts = ''
            if execution_data[input_item_ts] == "None":
                input_data_ts = ''
            else:
                input_data_ts = str(execution_data[input_item_ts]).replace('\n','\\n')
            input_item_ts = str(input_items_for_test_step[input_item_ts]).replace('field_input_value',input_data_ts)
            input_item_ts = eval(input_item_ts)
            ts_playload.update(input_item_ts['input_playload'])
    logging.info('step id  - %s' %str(execution_data['StepId']))
    logging.info('test step infomation - %s' %str(ts_playload))
    result = rh.updateStep(stepid= execution_data['StepId'], playloads=json.dumps(ts_playload))
    if result.status_code == 200:
        #logging.info(result.text)
        loggas.input_message(path = message_path,message = 'test step updated - %s' %str(execution_data['StepId']))
        status_update_step = True
    else:
        logging.info(result.text)
        loggas.input_message(path = message_path,message = 'test step updated error - %s - %s' %(str(execution_data['StepId']),result.text))
    return status_update_step
