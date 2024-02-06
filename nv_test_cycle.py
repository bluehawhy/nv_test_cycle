import sys, os
from PyQt5.QtWidgets import QApplication


#add internal libary
from _src import test_cycle_ui, test_cycle

refer_api = "local"
#refer_api = "global"

if refer_api == "global":
    sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
    from _api import loggas, configus
if refer_api == "local":
    from _src._api import loggas, configus


logging= loggas.logger

logging_file_name = loggas.log_full_name

version = 'Test Cycle v1.21'
revision_list=[
    'Revision list',
    'v0.1 (2022-12-24) : proto type release (beta ver.)',
    'v0.2 (2023-01-17) : add time to stay for loading page.',
    '                    exception if update fail of step comment',
    'v0.3 (2023-03-20) : exception if loading fail.',
    'v0.4 (2023-03-28) : modify data file.',
    'v0.5 (2023-04-19) : add update result value ',
    'v0.5 (2023-04-19) : pass update if element not found',
    'v0.51 (2023-04-21) : bugfix during step comment update',
    'v1.0 (2023-04-21) : use of REST (import) and selenium',
    'v1.1 (2023-09-21) : use of REST (import) and selenium',
    'v1.2 (2023-10-16) : bug fix of finding test step id',
    'v1.21 (2024-02-02) : modify function to reduce selenium search'
    ]

config_path ='static\config\config.json'
config_data =configus.load_config(config_path)
message_path = config_data['message_path']

def start_app():
    loggas.remove_message(message_path)
    loggas.input_message(path = message_path, message = version)
    for revision in revision_list:
        loggas.input_message(path = message_path, message = revision)
    app = QApplication(sys.argv)
    ex = test_cycle_ui.MyMainWindow(version)
    sys.exit(app.exec_())

def debug_app():
    test_cycle.update_test_cycle('test.xlsx')

 
if __name__ =='__main__':
    start_app()