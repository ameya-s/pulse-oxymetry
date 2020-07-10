import max30100
import json
import time
import numpy as np


def get_last_k_readings(data, var, kernel_size):
    x = list(data.items())
    x.reverse()
    return np.array([v[var] for i, v in x if i > len(x) - kernel_size - 1])


def main():
    mx30 = max30100.MAX30100(led_current_red=40.2, led_current_ir=27.1)
    mx30.set_mode(max30100.MODE_SPO2)
    mx30.enable_spo2()
    data = {}
    t_vec, red_vec = [], []

    i = 0
    j = 0
    while True:
        if i > 5000:
            break
        try:
            mx30.read_sensor()
            print('i => ', i)
            print(mx30.ir, mx30.red)

            data[i] = {}
            data[i]['tst'] = round(time.time() * 1000)
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

            # # Butterworth filter
            # if i>0:
            #     data[i]['butter_ir'] =

            if j < 400 * (i+1):
                t_vec.append(data[i]['tst'])
                red_vec.append(data[i]['red'])
                heart_rate(t_vec,red_vec)
                j += 1
            i += 1

        except IOError:
            print('IO error : error in reading')

    with open('data_dump_spo2.json', 'w') as f:
        f.write(json.dumps(data))


def heart_rate(t_vec, red_vec):
    print("=============== t_vec  =============")
    print(t_vec)

    print("=============== red_vec  =============")
    print(red_vec)

    heart_rate_span = [10, 250]  # max span of heart rate
    pts = 1800  # points used for peak finding (400 Hz, I recommend at least 4s (1600 pts)
    smoothing_size = 20  # convolution smoothing size

    # convolve, calculate gradient, and remove bad endpoints

    t_vals, y_vals = [], []

    samp_rate = 1 / np.mean(np.diff(t_vals))  # average sample rate for determining peaks
    min_time_bw_samps = (60.0 / heart_rate_span[1])

    t_vals = t_vec
    y_vals = red_vec

    y_vals = np.convolve(y_vals, np.ones((smoothing_size,)), 'same') / smoothing_size

    print("=============== t_vals  =============")
    print(t_vals)

    print("=============== y_vals  =============")
    print(y_vals)

    red_grad = np.gradient(y_vals, t_vals)

    red_grad[0:int(smoothing_size / 2) + 1] = np.zeros((int(smoothing_size / 2) + 1,))
    red_grad[-int(smoothing_size / 2) - 1:] = np.zeros((int(smoothing_size / 2) + 1,))

    y_vals = np.append(np.repeat(y_vals[int(smoothing_size / 2)], int(smoothing_size / 2)),
                       y_vals[int(smoothing_size / 2):-int(smoothing_size / 2)])
    y_vals = np.append(y_vals, np.repeat(y_vals[-int(smoothing_size / 2)], int(smoothing_size / 2)))

    # peak locator algorithm
    peak_locs = np.where(red_grad < -np.std(red_grad))
    # if len(peak_locs[0])==0:
    #     continue

    prev_pk = peak_locs[0][0]
    true_peak_locs, pk_loc_span = [], []
    for ii in peak_locs[0]:
        y_pk = y_vals[ii]
        if (t_vals[ii] - t_vals[prev_pk]) < min_time_bw_samps:
            pk_loc_span.append(ii)
        else:
            if pk_loc_span == []:
                true_peak_locs.append(ii)
            else:
                true_peak_locs.append(int(np.mean(pk_loc_span)))
                pk_loc_span = []

        prev_pk = int(ii)

    t_peaks = [t_vals[kk] for kk in true_peak_locs]
    # if t_peaks==[]:
    #     continue
    # else:
    print('BPM: {0:2.1f}'.format(60.0 / np.mean(np.diff(t_peaks))))

    # time.sleep(0.005)


if __name__ == "__main__":
    main()
