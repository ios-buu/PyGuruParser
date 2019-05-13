# code=utf-8
import matplotlib as mpl

mpl.use('TkAgg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import acf, pacf, plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARMA
from suppose.parser import Method, Info, Request, Response, Uri
from suppose import parser
import itertools
import seaborn as sns


def tsplot(y, lags=None, title='', figsize=(14, 8)):
    fig = plt.figure(figsize=figsize)
    layout = (2, 2)
    ts_ax = plt.subplot2grid(layout, (0, 0))
    hist_ax = plt.subplot2grid(layout, (0, 1))
    acf_ax = plt.subplot2grid(layout, (1, 0))
    pacf_ax = plt.subplot2grid(layout, (1, 1))

    y.plot(ax=ts_ax)
    ts_ax.set_title(title)
    y.plot(ax=hist_ax, kind='hist', bins=25)
    hist_ax.set_title('Histogram')
    plot_acf(y, lags=lags, ax=acf_ax)
    plot_pacf(y, lags=lags, ax=pacf_ax)
    [ax.set_xlim(0) for ax in [acf_ax, pacf_ax]]
    sns.despine()
    plt.tight_layout()
    return ts_ax, acf_ax, pacf_ax


def parse_xy_to_array(x, y):
    result = []
    for elem_x, elem_y in zip(x, y):
        result.append([elem_x, elem_y])
    return result


def confirm_layer(temp_x, y):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    # 阶数
    time_series.plot(figsize=(10, 6))

    fig = plt.figure(figsize=(6, 6))

    ax1 = fig.add_subplot(161)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax1.plot(time_series)

    ax2 = fig.add_subplot(162)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax2.plot(time_series.diff(1))

    ax3 = fig.add_subplot(163)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax3.plot(time_series.diff(2))

    ax3 = fig.add_subplot(164)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax3.plot(time_series.diff(3))
    ax3 = fig.add_subplot(165)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax3.plot(time_series.diff(4))
    ax3 = fig.add_subplot(166)
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x, rotation=45)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    ax3.plot(time_series.diff(5))
    plt.show()


def confirm_pq_step_1(temp_x, y, d, title):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    tsplot(time_series if d == 0 else time_series.diff(d), title=title, lags=36)
    plt.show()


def confirm_pq_step_2(temp_x, y):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    # 热力图
    p_min = 0
    d_min = 0
    q_min = 0
    p_max = 8
    d_max = 0
    q_max = 8

    # Initialize a DataFrame to store the results,，以BIC准则
    results_bic = pd.DataFrame(index=['AR{}'.format(i) for i in range(p_min, p_max + 1)],
                               columns=['MA{}'.format(i) for i in range(q_min, q_max + 1)])

    for p, d, q in itertools.product(range(p_min, p_max + 1),
                                     range(d_min, d_max + 1),
                                     range(q_min, q_max + 1)):
        if p == 0 and d == 0 and q == 0:
            results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = np.nan
            continue

        try:
            model = sm.tsa.ARIMA(time_series, order=(p, d, q),
                                 # enforce_stationarity=False,
                                 # enforce_invertibility=False,
                                 )
            results = model.fit()
            results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = results.bic
        except:
            continue
    results_bic = results_bic[results_bic.columns].astype(float)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax = sns.heatmap(results_bic,
                     mask=results_bic.isnull(),
                     ax=ax,
                     annot=True,
                     fmt='.2f',
                     )
    ax.set_title('BIC')
    plt.show()
    # AR0 MA1


def confirm_pq_step_3(temp_x, y, max_ar, max_ma):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    # 定pq
    train_results = sm.tsa.arma_order_select_ic(time_series, ic=['aic', 'bic'], trend='nc', max_ar=max_ar,
                                                max_ma=max_ma)
    print('AIC', train_results.aic_min_order)
    print('BIC', train_results.bic_min_order)
    return train_results.bic_min_order


def predict(temp_x, y, p, q, d):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    print(f'p={p} d={d} q={q}')
    # 定pq
    model_results = sm.tsa.ARIMA(time_series, order=(p, d, q)).fit()  # (p,d,q)
    predict_sunspots = model_results.predict(dynamic=False)
    print(predict_sunspots)
    fig, ax = plt.subplots()
    ax = time_series.plot(ax=ax)
    ax = predict_sunspots.plot(ax=ax)

    # 生成一份模型报告
    print(model_results.summary2())
    plt.show()
    # 预测至2020年， 返回预测结果， 标准误差， 和置信区间
    time_predict_data = model_results.forecast((pd.to_datetime('2019-12-31', format='%Y-%m-%d') - pd.to_datetime(
        x[len(x) - 1], format='%Y-%m-%d')).components.days)
    time_predict = pd.Series(time_predict_data[0])
    temp_x = []
    for date in pd.date_range(start=x[len(x) - 1], end='2019-12-31')[1:]:
        temp_x.append(str(date))
    time_predict.index = pd.Index(temp_x)
    time_predict.plot()
    plt.show()


def auto(x, y, title):
    confirm_layer(x, y)
    reconfirm = 1
    d = 0
    while reconfirm == 1:
        d = int(input('请输入阶数：'))
        confirm_pq_step_1(x, y, d, title)
        reconfirm = int(input('是否重新定阶（0-否 1-是）：'))
    confirm_pq_step_2(x, y)
    max_ar = int(input('请输入ar最大值：'))
    max_ma = int(input('请输入ma最大值：'))
    p, q = confirm_pq_step_3(x, y, max_ar, max_ma)
    predict(x, y, p, q, d)

    repredict = 1
    while repredict == 1:
        repredict = input('是否重新定参数（0-否 1-是）：')
        if repredict == 0:
            break
        d = int(input('请输入阶数：'))
        p = int(input('请输入p：'))
        q = int(input('请输入q：'))
        predict(x, y, p, q, d)


def uri_layer_temp(temp_x, y):
    x = []
    for date in temp_x:
        x.append(date.replace('"', '').split('+')[0].split(' ')[0])
    time_series = pd.Series(y)
    time_series.index = pd.Index(x)
    # 阶数
    # time_series.plot(figsize=(10, 6))
    #
    # fig = plt.figure(figsize=(6, 6))
    #
    # ax1 = fig.add_subplot(161)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax1.plot(time_series)
    #
    # ax2 = fig.add_subplot(162)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax2.plot(time_series.diff(1))
    #
    # ax3 = fig.add_subplot(163)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax3.plot(time_series.diff(2))
    #
    # ax3 = fig.add_subplot(164)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax3.plot(time_series.diff(3))
    # ax3 = fig.add_subplot(165)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax3.plot(time_series.diff(4))
    # ax3 = fig.add_subplot(166)
    # ind = np.arange(len(x))
    # locs, labels = plt.xticks(ind, x,rotation=45)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)
    # ax3.plot(time_series.diff(5))

    tsplot(y, title='Consumer Sentiment', lags=36)
    plt.show()
    # 热力图
    # p_min = 0
    #
    # d_min = 0
    #
    # q_min = 0
    #
    # p_max = 5
    #
    # d_max = 0
    #
    # q_max = 5
    #
    # # Initialize a DataFrame tostorethe results,，以BIC准则
    #
    # results_bic = pd.DataFrame(index=['AR{}'.format(i) for i in range(p_min, p_max + 1)],
    #                            columns=['MA{}'.format(i) for i in range(q_min, q_max + 1)])
    # for p, d, q in itertools.product(range(p_min, p_max + 1), range(d_min, d_max + 1), range(q_min, q_max + 1)):
    #     if p == 0 and d == 0 and q == 0:
    #         results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = np.nan
    #         continue
    #     try:
    #         model = sm.tsa.ARIMA(time_series, order=(p, d, q)
    #                              # enforce_stationarity=False,
    #                              # enforce_invertibility=False,
    #                              )
    #
    #         results = model.fit()
    #         results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = results.bic
    #     except:
    #         continue
    # results_bic = results_bic[results_bic.columns].astype(float).idxmin()
    # fig, ax = plt.subplots(figsize=(10, 8))
    # ax = sns.heatmap(results_bic, mask=results_bic.isnull(), ax=ax, annot=True, fmt='.2f', )
    # ax.set_title('BIC')
    # plt.show()
    # 参数状态
    # t = sm.tsa.stattools.adfuller(time_series, )
    # output = pd.DataFrame(
    #     index=['Test Statistic Value', "p-value", "Lags Used", "Number of Observations Used", "Critical Value(1%)",
    #            "Critical Value(5%)", "Critical Value(10%)"], columns=['value'])
    # output['value']['Test Statistic Value'] = t[0]
    # output['value']['p-value'] = t[1]
    # output['value']['Lags Used'] = t[2]
    # output['value']['Number of Observations Used'] = t[3]
    # output['value']['Critical Value(1%)'] = t[4]['1%']
    # output['value']['Critical Value(5%)'] = t[4]['5%']
    # output['value']['Critical Value(10%)'] = t[4]['10%']
    # print(output)

    # pq组合
    # pmax = int(len(time_series) / 10)  # 一般阶数不超过 length /10
    # qmax = int(len(time_series) / 10)
    # bic_matrix = []
    # for p in range(pmax + 1):
    #     temp = []
    #     for q in range(qmax + 1):
    #         try:
    #             temp.append(sm.tsa.ARIMA(time_series, (p, 1, q)).fit().bic)
    #         except:
    #             temp.append(None)
    #         bic_matrix.append(temp)
    #
    # bic_matrix = pd.DataFrame(bic_matrix)  # 将其转换成Dataframe 数据结构
    # p_min = 0
    #
    # d_min = 0
    #
    # q_min = 0
    #
    # p_max = 5
    #
    # d_max = 0
    #
    # q_max = 5
    #
    # # Initialize a DataFrame tostorethe results,，以BIC准则
    #
    # results_bic = pd.DataFrame(index=['AR{}'.format(i) for i in range(p_min, p_max + 1)],
    #                            columns=['MA{}'.format(i) for i in range(q_min, q_max + 1)])
    # for p, d, q in itertools.product(range(p_min, p_max + 1), range(d_min, d_max + 1), range(q_min, q_max + 1)):
    #     if p == 0 and d == 0 and q == 0:
    #         results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = np.nan
    #         continue
    #     try:
    #         model = sm.tsa.ARIMA(time_series, order=(p, d, q)
    #                              # enforce_stationarity=False,
    #                              # enforce_invertibility=False,
    #                              )
    #
    #         results = model.fit()
    #         results_bic.loc['AR{}'.format(p), 'MA{}'.format(q)] = results.bic
    #     except:
    #         continue
    # p, q = results_bic[results_bic.columns].astype(float).idxmin()
    # print(u'BIC 最小的p值 和 q 值：%s,%s' % (p, q))  # BIC 最小的p值 和 q 值：0,1
    # # 所以可以建立ARIMA 模型，ARIMA(0,1,1)
    # model = sm.tsa.ARIMA(time_series, (p, 1, q)).fit()
    # # 生成一份模型报告
    # print(model.summary2())
    # # 为未来730天进行预测， 返回预测结果， 标准误差， 和置信区间
    # temp_x = pd.date_range(start=x[len(x)-1],end='2020-12-31')[1:]
    # time_predict = model.forecast((pd.to_datetime('2020-12-31', format='%Y-%m-%d') - pd.to_datetime(x[len(x) - 1],format='%Y-%m-%d')).components.days)
    # temp_y = time_predict[0]
    # plt.plot(temp_x, temp_y)
    # for label in labels:
    #     label.set_visible(False)
    # for label in labels[::20]:
    #     label.set_visible(True)

    # plt.show()
    # predict_sunspots = results.forecast()
    # print(predict_sunspots)
    pass
