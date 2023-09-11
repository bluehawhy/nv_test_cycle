#!/usr/bin/python
import os, sys
import threading
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, QTimer, QTime

from PyQt5.QtGui import QTextCursor
from datetime import date


#add internal libary
from _src import test_cycle

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from _api import loggas, zyra, configus
#from _src._api import logger, jira_rest, config, logging_message


logging = loggas.logger
logging_file_name = loggas.log_full_name

config_path ='static\config\config.json'
message_path = configus.load_config(config_path)['message_path']
qss_path  = configus.load_config(config_path)['qss_path']

logging.debug('qss_path is %s' %qss_path)
logging.debug('config_path is %s' %config_path)

class MyMainWindow(QMainWindow):
    def __init__(self,title):
        super().__init__()
        self.title = title
        self.today = date.today().strftime('%Y%m%d')
        self.setStyleSheet(open(qss_path, "r").read())
        self.initUI()
        self.show()

    def initUI(self):
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(self.title)
        self.setGeometry(200,200,1000,1200)
        #self.setFixedSize(600, 480)
        self.form_widget = FormWidget(self, self.statusBar())
        self.setCentralWidget(self.form_widget)


class FormWidget(QWidget):
    def __init__(self, parent,statusbar):
        super(FormWidget, self).__init__(parent)
        self.statusbar_status = 'not logged in'
        self.session_info = None
        self.logging_temp = None
        self.statusbar = statusbar
        self.initUI() 
        self.show()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.thread_ui)
        self.timer.start(1000)

    def initUI(self):
        self.setStyleSheet(open(qss_path, "r").read())
        # call layout
        self.layout_main = QVBoxLayout(self)
        self.login_layout = QHBoxLayout(self)
        self.login_layout_id_pw = QGridLayout(self)
        


        #set user data
        config_data =configus.load_config(config_path)
        self.user = config_data['id']
        self.password = config_data['password']
        self.line_id = QLineEdit(self.user)       
        self.line_password = QLineEdit(self.password)
        self.line_password.setEchoMode(QLineEdit.Password)
        self.button_login_import = QPushButton('Log In')
        self.button_login_import.setFixedHeight(60)
        self.button_sync_test_file = QPushButton('sync files')
        self.button_sync_test_file.setFixedHeight(60)
        self.login_layout_id_pw.addWidget(QLabel('ID') , 1, 0)
        self.login_layout_id_pw.addWidget(QLabel('Password') , 2, 0)
        self.login_layout_id_pw.addWidget(self.line_id, 1, 2)
        self.login_layout_id_pw.addWidget(self.line_password, 2, 2)
        
        #set chrome UI layout
        self.chrome_radio_layout = QHBoxLayout(self)
        self.chrome_radio_layout.addWidget(QLabel('chrome'))
        self.chrome_config = config_data['headless']
        for self.chrome in ['True','False']:
            self.radiobutton_chrome = QRadioButton(self.chrome)
            self.radiobutton_chrome.value = self.chrome
            if self.chrome == self.chrome_config:
                self.radiobutton_chrome.setChecked(True)
            self.chrome_radio_layout.addWidget(self.radiobutton_chrome)
            self.radiobutton_chrome.toggled.connect(self.on_radiobutton_chrome_clicked)

        #self.login_layout.addWidget(self.button_sync_test_file)
        self.login_layout.addLayout(self.login_layout_id_pw)
        self.login_layout.addWidget(self.button_login_import)
        self.login_layout.addLayout(self.chrome_radio_layout)
        

        # add log layout
        self.qtext_log_browser = QTextBrowser()
        self.qtext_log_browser.setReadOnly(1)

        #set main layout
        self.layout_main.addLayout(self.login_layout)
        
        self.layout_main.addWidget(self.qtext_log_browser)
        self.setLayout(self.layout_main)

        #login / import event
        self.button_login_import.clicked.connect(self.on_start)
        self.line_password.returnPressed.connect(self.on_start)
        
    # add event list
    def open_fileName_dialog(self):
        config_data =configus.load_config(config_path)
        set_dir = config_data['last_file_path']
        logging.info(set_dir)
        if set_dir == '':
            set_dir = os.path.join(os.path.expanduser('~'),'Desktop')
            logging.info('folder path is %s' %set_dir)
        else:
            logging.info('folder path is %s' %set_dir)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self,  "Open Logwork", set_dir, "Excel Files (*.xlsx)",options=options)
        if file_name == '':
            folder_path = set_dir
        else:
            folder_path = os.path.dirname(file_name)
        logging.debug('file path is %s' %file_name)
        logging.debug('folder path is %s' %folder_path)
        config_data['last_file_path']=folder_path
        logging.debug(config_data)
        config_data = configus.save_config(config_data,config_path)
        return file_name

    #set tread to change status bar and log browser
    def thread_ui(self):
        def show_time_statusbar():
            self.statusbar_time = QTime.currentTime().toString("hh:mm:ss")
            self.statusbar_message = self.statusbar_time + '\t-\t' + self.statusbar_status  
            self.statusbar.showMessage(str(self.statusbar_message))
          
        def show_logging():
            with open(message_path, 'r') as myfile:
                self.logging = myfile.read()
            if self.logging_temp == self.logging:
                pass
            else:
                self.qtext_log_browser.setText(self.logging)
                self.logging_temp = self.logging
                self.qtext_log_browser.moveCursor(QTextCursor.End)
        show_time_statusbar()
        show_logging()
        return 0

    @pyqtSlot()
    def on_radiobutton_chrome_clicked(self):
        config_data =configus.load_config(config_path)
        radioButton = self.sender()
        if radioButton.isChecked():
            logging.info(f'{radioButton.value} clicked')
            config_data['headless'] = radioButton.value
            config_data = configus.save_config(config_data,config_path)
        return 0


    @pyqtSlot()
    def on_start(self):
        config_data =configus.load_config(config_path)
        if self.statusbar_status == 'not logged in':
            loggas.input_message(path = message_path,message = 'current not login, start login')
            self.user = self.line_id.text()
            self.password = self.line_password.text()
            self.session, self.session_info, self.status_login = zyra.initsession(username= self.user, password= self.password, jira_url= config_data['jira_url'])
            #fail to login
            if self.status_login is False:
                QMessageBox.about(self, "Login Fail", "please check your password or internet connection")
            #if loggin success
            else:
                self.button_login_import.setText('Import\nTest Cycle')
                self.statusbar_status = 'logged in'
                loggas.input_message(path = message_path,message = 'user (%s) is logged in' %self.user)
                config_data['id'] = self.user
                config_data['password'] = self.password
                config_data = configus.save_config(config_data,config_path)
                self.line_id.setReadOnly(1)
                self.line_password.setReadOnly(1)
        else:
            loggas.input_message(path = message_path, message = 'already logged in, start Test Cycle import~!')
            
            def import_test_cycle():
                self.button_login_import.setEnabled(False)
                #make session
                try:
                    test_cycle.update_test_cycle(self.file_name)
                except Exception as inst:
                    logging.debug(type(inst))
                    logging.debug(inst)
                    logging.debug(traceback.format_exc())
                    loggas.input_message(path = message_path,message = "there is errer at the point - %s" %str(inst))
                finally:
                    self.button_login_import.setEnabled(True)
                    self.statusbar_status = 'Test Cycle importing done.'
                return 0
            
            self.file_name = self.open_fileName_dialog()
            logging.info(self.file_name)
            flie_ext = os.path.splitext(self.file_name)[1]
            if flie_ext in ['.xlsx','.xlsm','.xltx','.xltm']:
                self.statusbar_status = 'Test Cycle importing~'
                thread_import = threading.Thread(target=import_test_cycle)
                thread_import.start()
            else:
                loggas.input_message(path = message_path, message = f'please check file name - {self.file_name}')
        return 0



        
