import os
import pandas as pd

def read_tc_file(file_path):
    df_tc = None
    flie_ext = os.path.splitext(file_path)[1]
    if flie_ext == '.csv':
        df_tc = pd.read_csv(file_path)
    if flie_ext == '.xlsx':
        df_tc = pd.read_excel(file_path)
    return df_tc

def sync_result(old_file, new_file):
    df_new = read_tc_file(new_file)
    df_old = read_tc_file(old_file)
    modi_file = os.path.splitext(new_file)[0]+'_modi.xlsx'
    for i in range(len(df_old)):
        #get issue ket and OrderId
        issue_key = df_old.loc[i]['Issue Key']
        OrderId = df_old.loc[i]['OrderId']
        #change
        def sync_df(column_name):
            old_value = df_old.loc[(df_old['Issue Key'] == issue_key) & (df_old['OrderId'] == OrderId), column_name]
            df_new.loc[(df_new['Issue Key'] == issue_key) & (df_new['OrderId'] == OrderId), column_name] = old_value
        sync_df('ExecutionStatus')
        sync_df('Comment')
        sync_df('ExecutionDefects')
        sync_df('Step Result')
        sync_df('Comments')
    df_new['tc_imported'] = False
    df_new.to_excel(modi_file)
    return modi_file