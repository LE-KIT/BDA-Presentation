import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
import numpy as np
import datetime

def plot_and_calculate_error(df_predictions,df_true_test_values,cols):
    
    for col in cols:
        plt.figure(figsize=[20,10])
        plt.plot(df_predictions['Tag'],df_predictions[col])
        plt.plot(df_true_test_values['Tag'],df_true_test_values[col])
        plt.title("Time Series Prediction Country {} for May ".format(col))
        plt.legend(['Prediction','True Data'])
        plt.show()
        
    Y=df_true_test_values[cols] 
    Y_hat=df_predictions[cols]
    
    mae = np.abs(Y - Y_hat).mean()
    print("MAE:\n{}\n\nGesamt:{}".format(mae,mae.mean()))