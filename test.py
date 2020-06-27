import max30100
import json
import time

mx30 = max30100.MAX30100()

mx30.set_mode(max30100.MODE_SPO2)
mx30.enable_spo2()
data = {}
raw_readings_ir, raw_readings_red = [], []
interm_readings_ir = []
filter_dc_ir = []

i = 0
while True:
    if i>5000: break
    try:
        mx30.read_sensor()
        print('i => ', i)
        print(mx30.ir, mx30.red)

        data[i] = {}
        data[i]['timestamp'] = time.time_ns()
        data[i]['ir'] = mx30.ir
        data[i]['red'] = mx30.red

        i += 1
    except IOError:
        print('IO error : error in reading')

with open('data_dump_spo2.json', 'w') as f:
    f.write(json.dumps(data))

