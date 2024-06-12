import sys
import numpy as np
from scipy import stats


def check_file_ending(path):
    file_ending = path.split(".")[-1]
    print("     ending", file_ending)
    return file_ending == "npy"


def open_file(file_path):
    array = np.load(file_path)
    if array.shape[1] == 4:
        array = array[:,-1:]

    # print("quantile 0.25:", np.quantile(array,[0.1]))
    # print("quantile 0.75:", np.quantile(array,[0.75,1]))
    print("quantile 0.25:", np.percentile(array,25))
    print("quantile 0.75:", stats.mstats.mquantiles(array,[0.75]))
    print("interquartile:", stats.iqr(array))
    print("mean:", np.mean(array))
    print("median:", np.median(array))


def concat_arrays(list_of_arrays):
    concat_list = []
    for array in list_of_arrays:
        array = np.load(array).flatten()
        concat_list.extend(array)
    return concat_list

if __name__ == "__main__":
    inputs = sys.argv[1:]
    for input in inputs:
        print(f"## Opening {input} ##")
        if check_file_ending(input):
            open_file(input)
        else:
            print("     --> wrong filetype")