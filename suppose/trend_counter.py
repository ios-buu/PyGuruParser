# code=utf-8
import matplotlib as mpl
mpl.use('TkAgg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import acf,pacf,plot_acf,plot_pacf
from statsmodels.tsa.arima_model import ARMA

def uri_layer(x,y):
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    time_series.plot(figsize=(12, 8))
    # time_series = np.log(time_series)
    # time_series.plot(figsize=(8, 6))
    plt.show()
    pass
uri_layer([1,2,3],[1,2,3])
def api_resource(x,y):
    pass


def endpoint(x,y):
    pass


def method(x,y):
    pass


def response_layer(x,y):
    pass


def request_restriction(x,y):
    pass


def request_param(x,y):
    pass


def request_param_location(x,y):
    pass
