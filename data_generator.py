import json
import random

data = dict()
for i in range(300):
    data[i] = dict()
    data[i]['status'] = {'速度': f'{round(1000 * random.random()) / 100}m/s', '长宽比': f'{round(600 * random.random()) / 100}'}
    if random.random() > 0.1:
        data[i]['warnning'] = ''
    else:
        data[i]['warnning'] = 'WARNNING'

with open('data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
