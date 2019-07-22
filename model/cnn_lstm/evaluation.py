import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
import numpy as np
import datetime

def plot_predictions(df_predictions,df_true_test_values,cols):
    
    for col in cols:
        
        fig = plt.figure(figsize=[20,10])
        fig.suptitle("Time Series Prediction Country {} for May ".format(col), fontsize=16)

        plt.subplot(311)
        plt.plot(df_predictions['Prophet_'+col],'--')
        plt.plot(df_true_test_values[col])
        plt.legend(['Prophet','True Data'])

        plt.subplot(312)
        plt.plot(df_predictions['LSTM_'+col],'--')
        plt.plot(df_true_test_values[col])
        plt.legend(['LSTM','True Data'])

        plt.subplot(313)
        plt.plot(df_predictions['CNNLSTM_'+col],'--')
        plt.plot(df_true_test_values[col])
        plt.legend(['CNN LSTM','True Data'])
        plt.show()

def calculate_prediction_errors(df_predictions,df_true_eval_values,cols):
    error_scale = np.abs(df_true_eval_values.sum())/np.abs(df_true_eval_values.sum()).sum()

    for model_prefix in ['Prophet_','LSTM_','CNNLSTM_']:
        columns = [model_prefix+col for col in cols]
        y_hat = df_predictions[columns]
        y = df_true_eval_values.values

        rse_scaled = np.sqrt( ((y-y_hat)**2).sum() ) * error_scale.values
        rmse_scaled = np.sqrt( ((y-y_hat)**2).mean() ) * error_scale.values
        print('{} Scaled RSE: {}'.format(model_prefix.split('_')[0] , rse_scaled.sum()))
        print('{} Scaled RMSE: {}'.format(model_prefix.split('_')[0], rmse_scaled.mean()))


    