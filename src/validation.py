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
import pysmile_license
import logging


def validateWithSMILE(dataFn, modelFN, nFold, outcomeID, targetNodeId):
    logger = logging.getLogger('validateWithSMILE')
    net = pysmile.Network()
    net.read_file(modelFN)
    ds = pysmile.learning.DataSet()
    ds.read_file(dataFn)
    # net = pysmile.Network()
    # load network and data here
    matching = ds.match_network(net)
    # ===============================================
    validator = pysmile.learning.Validator(net, ds, matching)
    targetClassNodehandle = net.get_node(targetNodeId)
    try:
        validator.add_class_node(targetNodeId)
    except pysmile.SMILEException as e:
        print(f'targetNodeId = {targetNodeId}')
        print(f'targetClassNodehandle = {targetClassNodehandle}')
        print(f'{e}')
        logger.error(f'{e}')
        print('=======================================')
    except Exception as e:
        print(f'targetNodeId = {targetNodeId}')
        print(f'targetClassNodehandle = {targetClassNodehandle}')
        print(f'{e}')
        logger.error(f'{e}')
        print('=======================================')
    finally:
        logger.debug(f'Validation successfully completed')
    # ===============================================
    em = pysmile.learning.EM()
    # optionally tweak EM options here
    logger.debug(f'Running {nFold}-fold crossvalidation with SMILE')
    validator.k_fold(em, nFold)
    logger.debug(f'Finished {nFold}-fold crossvalidation with SMILE')

    acc = validator.get_accuracy(targetClassNodehandle, outcomeID)
    return acc


def main():
    modelFN = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl"
    # dataFn = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA.csv"
    outcomeID = 1
    nFold = 5
    targetNodeId = "AKI48H"
    accuracyK_Fold = validateWithSMILE(dataFn, modelFN, nFold, outcomeID, targetNodeId)
    print(f"accuracyK_Fold = {accuracyK_Fold}")
    print('END')


if __name__ == '__main__':
    main()
