import max30100
import json
import time
import numpy as np


def get_last_k_readings(data, var, kernel_size):
    x = list(data.items())
    x.reverse()
    return np.array([v[var] for i, v in x if i > len(x) - kernel_size - 1])


def main():
    mx30 = max30100.MAX30100(led_current_red=50.0, led_current_ir=50.0)
    mx30.set_mode(max30100.MODE_SPO2)
    mx30.enable_spo2()
    data = {}

    i = 0
    while True:
        if i > 5000:
            break
        try:
            mx30.read_sensor()
            print('i => ', i)
            print(mx30.ir, mx30.red)

            data[i] = {}
            data[i]['timestamp'] = time.time()
            data[i]['ir'] = mx30.ir
            data[i]['red'] = mx30.red

            # DC Removal
            if i == 0:
                data[i]['w_ir'] = data[i]['ir']
                data[i]['result_ir'] = data[i]['w_ir']

                data[i]['w_red'] = data[i]['red']
                data[i]['result_red'] = data[i]['w_red']
            else:
                data[i]['w_ir'] = data[i]['ir'] + 0.95 * data[i - 1]['w_ir']
                data[i]['result_ir'] = data[i]['w_ir'] - data[i - 1]['w_ir']

                data[i]['w_red'] = data[i]['red'] + 0.95 * data[i - 1]['w_red']
                data[i]['result_red'] = data[i]['w_red'] - data[i - 1]['w_red']

            # Mean Filter
            kernel_size = 10
            last_k_readings_ir = get_last_k_readings(data, 'result_ir', kernel_size)
            data[i]['mean_ir'] = last_k_readings_ir.mean()

            last_k_readings_red = get_last_k_readings(data, 'result_red', kernel_size)
            data[i]['mean_red'] = last_k_readings_red.mean()

            # Butterworth filter
            if i>0:
                data[i]['butter_ir'] =

            i += 1
        except IOError:
            print('IO error : error in reading')

    with open('data_dump_spo2.json', 'w') as f:
        f.write(json.dumps(data))


if __name__ == "__main__":
    main()
