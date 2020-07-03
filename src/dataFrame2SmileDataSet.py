import param4BN_learn_from_data_tranfs
import pysmile
import pysmile_license

def main():
    nrows = 3
    dataWONanFN = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    dataWONaN = param4BN_learn_from_data_tranfs.readData(dataWONanFN, nrows)
    # ***********************************
    dfTypes =  dataWONaN.dtypes
    # ***********************************
    ds = pysmile.learning.DataSet()



    print(f'')

if __name__ == '__main__':
    main()
