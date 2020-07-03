import argparse
import pandas as pd
import numpy as np

if __name__ == "__main__":
    def main():
        dataFn = params.inputDataSetFile
        nrows = nFold = params.nRows
        df = pd.read_csv(dataFn, nrows=nrows)
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("--fds", action="store", dest="inputDataSetFile", type=str, default="xxxxxxxxxx",
                        help="file path to file with csv dataset file (default = 'C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_ri_0_ri2_217148_ro_93120_20-04-24_23-30-27_short.csv')")
    parser.add_argument("--nRows", action="store", dest="nRows", type=int, default=None,
                        help="# fold in crossvalidation n>0")

    params = parser.parse_args()  #
    print("*****************************")
    print("Input parameters:")
    print(params)
    print("*****************************")
    main()
