import argparse
import pandas as pd
import numpy as np

if __name__ == "__main__":
    def main():
        fn = params.inputDataSetFile
        nRows = params.numRows
        if nRows<0:
            nRows=None
        df = pd.read_csv(fn,nrows=nRows)
        df = df[df["subject_id"].notna()]
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("-n", action="store", dest="numRows", type=int, default=None,
                        help="number of rows to read")
    parser.add_argument("--fds", action="store", dest="inputDataSetFile", type=str, default='../../data/AKI_data_200325_full_dob_v02_test.csv',
                        help="file path to file with csv dataset file (default = '../../data/AKI_data_200325_full_dob_v02_test.csv')")



    params = parser.parse_args()  #
    print("*****************************")
    print("Input parameters:")
    print(params)
    print("*****************************")
    main()
