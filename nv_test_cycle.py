import os
import sys
from PyQt5.QtWidgets import QApplication

from _src._api import logger, logging_message, config
from _src import test_cycle_ui, test_cycle_selenium
logging= logger.logger

logging_file_name = logger.log_full_name

version = 'Test Cycle v0.51'
revision_list=[
    'Revision list',
    'v0.1 (2022-12-24) : proto type release (beta ver.)',
    'v0.2 (2023-01-17) : add time to stay for loading page.',
    '                    exception if update fail of step comment',
    'v0.3 (2023-03-20) : exception if loading fail.',
    'v0.4 (2023-03-28) : modify data file.',
    'v0.5 (2023-04-19) : add update result value ',
    'v0.5 (2023-04-19) : pass update if element not found',
    'v0.51 (2023-04-21) : bugfix during step comment update'
    ]

config_path ='static\config\config.json'
config_data =config.load_config(config_path)
message_path = config_data['message_path']

def start_app():
    logging_message.remove_message(message_path)
    logging_message.input_message(path = message_path, message = version)
    for revision in revision_list:
        logging_message.input_message(path = message_path, message = revision)
    app = QApplication(sys.argv)
    ex = test_cycle_ui.MyMainWindow(version)
    sys.exit(app.exec_())

def debug_app():
    path_modi_file = r'-'
    test_cycle_selenium.update_test_cycle(path_modi_file)

if __name__ =='__main__':
    start_app()

