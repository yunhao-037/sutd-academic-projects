import numpy as np
import datetime
import pickle
from libdw import pyrebase
import random
url = 'https://test-4f06e.firebaseio.com/'
apikey = 'AIzaSyBKnZs78dnlgJDbMRq_xmxt90oV8xf1BQ4'

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
def time_now():
    a = datetime.datetime.now()
    b = a.strftime('%H:%M:%S')
    return b
# minute counter
def minute_count(b):
    lst = b.split(':')
    count = int(lst[0]) * 60 + int(lst[1])
    return count
# column maker for numpy array
def column_maker(prev, now):
    column = []
    for i in range(60 * 24 + 1):
        if now > prev:
            if i >= prev and i <= now:
                column.append(1)
            else:
                column.append(0)
        elif now <= prev:
            if i >= prev or i <= now:
                column.append(1)
            else:
                column.append(0)
    return column
# main function
# data collection
def data_collect(machine, prev_time, now_time):
    try:
        with open('{}_data.txt'.format(machine), 'rb') as f:
            data = pickle.load(f)
    except:
        lst = []
        for i in range(60 * 24 + 1):
            lst.append(i)
        data = np.array([lst])
        with open('{}_data.txt'.format(machine), 'wb') as f:
            pickle.dump(data, f)
    newdata = [column_maker(prev_time, now_time)]
    # print(newdata)
    data = np.append(data, newdata, axis=0)
    # print(machine)
    # print(machine.shape)
    with open('{}_data.txt'.format(machine), 'wb') as f:
        pickle.dump(data, f)

def pred_use(machine, test_time):
    # test_time = minute_count(test_time)
    with open('{}_data.txt'.format(machine), 'rb') as f:
        data = pickle.load(f)
    count = 0
    for i in range(1, len(data[:, 0])):
        count += data[:, test_time][i]
    freq = (count / (len(data[:, test_time]) - 1)) * 100
    print(freq)
    if freq > 66:
        avail = 2
    elif freq > 33:
        avail = 1
    else:
        avail = 0
    return avail

def update_pyrebase(machine):
    for test_time in range(1441):
        avail = pred_use(machine,test_time)
        db.child('zpred').child(test_time).child(machine).set(avail)

