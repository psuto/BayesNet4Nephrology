import collections
from typing import Any, Union
import pandas as pd
import numpy as np
from numpy.core._multiarray_umath import ndarray
from pandas import Series
from pandas.core.arrays import ExtensionArray
import sys
import buildBNStructure
import param4BN_learn_from_data_tranfs as parBN
import pysmile


#     outDF2.to_csv('../../data/AKI_data_200325_full_dob_v02_forBN_w_NA.csv')
#     dfOutWONaN.to_csv('../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv')

def trainModel(net, fileName):
    ds = pysmile.learning.DataSet()
    ds.read_file(fileName)
    # net = pysmile.Network()
    # load network and data here
    matching = ds.match_network(net)
    em = pysmile.learning.EM()
    em.learn(ds, net, matching)
    print()

def main():
    dataWONanFN = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    dataWONaN = pd.read_csv(dataWONanFN)
    model = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl"
    net = pysmile.Network()
    net.read_file(model)
    trainModel(net, dataWONanFN)

    net.write_file("../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_trained.xdsl")
    print()

if __name__ == '__main__':
    main()