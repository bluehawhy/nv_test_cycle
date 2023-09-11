import sys, os
from PyQt5.QtWidgets import QApplication


#add internal libary
sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
from _api import loggas, configus
#from _src._api import loggas, configus

from _src import test_cycle_ui, test_cycle
logging= loggas.logger

logging_file_name = loggas.log_full_name

version = 'Test Cycle v1.0'
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
    'v1.1 (2023-09-21) : use of REST (import) and selenium'
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
    path_modi_file = r'C:/Users/Downloads/Smok.xlsx'
    test_cycle.update_test_cycle(path_modi_file)
 
if __name__ =='__main__':
    start_app()