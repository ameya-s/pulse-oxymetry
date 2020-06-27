import max30100
import json

mx30 = max30100.MAX30100()

#mx30.set_mode(max30100.MODE_SPO2)
#mx30.enable_spo2()
raw_readings_ir, raw_readings_red = [], []
interm_readings_ir = []
filter_dc_ir = []

i = 0
while True:
    if i>20000: break
    try:
        mx30.read_sensor()
        print('i => ', i)
        print(mx30.ir, mx30.red)

        raw_readings_ir.append(mx30.ir)
        raw_readings_red.append(mx30.red)
        if i==0:
            interm_readings_ir.append(raw_readings_ir[i])
            filter_dc_ir.append(interm_readings_ir[i])
        else:
            interm_readings_ir.append(raw_readings_ir[i] + 0.95 * interm_readings_ir[i - 1])
            filter_dc_ir.append(interm_readings_ir[i] - interm_readings_ir[i-1])
        i += 1
    except IOError:
        print('IO error : error in reading')


print(raw_readings_ir[2000:2020])
print(filter_dc_ir[2000:2020])

data_dict = {
    'raw_readings_ir' : raw_readings_ir,
    'raw_readings_red' : raw_readings_red,
    'interm_readings_ir' : interm_readings_ir,
    'filtered_dc_ir': filter_dc_ir
}

with open('data_dump_wo_spo2.json', 'w') as f:
    f.write(json.dumps(data_dict))

