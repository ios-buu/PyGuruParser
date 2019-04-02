# -*- coding: utf-8 -*-

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from suppose import counter
data_set = [
    ['query','/user/{id}',1,'get'],
    ['param','/user/{id}/auth',1,'get'],
    ['query','/user/{id}/auth',1,'get'],
    ['url','/doctor/{id}',2,'get'],
    ['param','/doctor/{id}',2,'get'],
    ['query', '/doctor/{id}', 2,'get'],
    ['param', '/doctor/{id}', 2,'get'],
    ['param', '/doctor/{id}', 2,'get'],
    ['param','/user/{id}',3,'get'],
    ['body', '/user/{id}', 3,'get'],
    ['param', '/user/{id}', 3,'get'],
    ['body', '/user/{id}', 3,'get'],
    ['body', '/user/{id}', 3,'get']
]
(x, category,y_list,x_,y_) = counter.count_request_param_location(data_set)

plt.subplot(1,2,1)
width = 0.35
ind = np.arange(len(x))
y_data = []
bottom = None
for y in y_list:
    pn = plt.bar(ind,y,width,bottom=bottom)
    if bottom is not None:
        bottom += np.array(y)
    else:
        bottom = y
    y_data.append(pn[0])

plt.xticks(ind,x)
plt.yticks(np.arange(0,max(bottom)+1,1))
plt.ylabel('The number of URL')
plt.xlabel('The fullname of location')
plt.title('The distribution of the location of Request Param')
plt.legend(y_data, category)


plt.subplot(1,2,2)
plt.xticks(ind,x_)
plt.yticks(np.arange(0,max(y_)+1,1))
plt.ylabel('The number of URL')
plt.xlabel('The number of location')
plt.title('The statistics of location in Request')
p1 = plt.bar(ind,y_,width)
plt.legend([p1[0]],['total'])
plt.show()
