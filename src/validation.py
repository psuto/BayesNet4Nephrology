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
import time
import json


def validateWithSMILE(dataFn, modelFN, nFold, outcomeID, targetNodeId):
    logger = logging.getLogger('validateWithSMILE')
    net = pysmile.Network()
    net.read_file(modelFN)
    ds = pysmile.learning.DataSet()
    ds.read_file(dataFn)
    recordCount = ds.get_record_count()
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
    print(f'Running {nFold}-fold crossvalidation with SMILE')
    t0 = time.time()
    print(f'{nFold}-starte at {time.strftime("%H:%M %y-%m-%d")}')
    validator.k_fold(em, nFold)
    deltaT = time.time() - t0
    print(f'Finished {nFold}-fold crossvalidation with SMILE in {deltaT} seconds')
    logger.debug(f'Finished {nFold}-fold crossvalidation with SMILE in {deltaT} seconds')
    acc = validator.get_accuracy(targetClassNodehandle, outcomeID)
    confMatrix = validator.get_confusion_matrix(targetNodeId)
    resultDS = validator.get_result_data_set()
    return ({'accuracy': acc, 'conMatrix': confMatrix, 'timeOfCrossValidation_sec': deltaT, 'recordCount': recordCount,
             'outcomeID': outcomeID}, resultDS)


def main():
    modelFN = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl"
    modelFN = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl"
    # dataFn = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    # dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_w_NA_20-04-14_14-35-01.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_20-04-14_14-35-01.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_20-04-14_15-13-35.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_w_NA_20-04-14_15-13-35.csv"
    outcomeID = 1
    nFold = 5  # 10
    targetNodeId = "AKI48H"
    jsonOutFN = f'..\output\paramsAndREsults_{parBN.timeStampStr}.json'
    jsonOutValidResultDSFN = f'..\output\validator_dsResults_{parBN.timeStampStr}.json'
    paramsJson = {'nFold': 10, 'targetNodeId': "AKI48H", 'outcomeID': outcomeID, 'inputFile': dataFn,
                  'modelFN': modelFN}
    perfMeassures_kFold, resultDS = validateWithSMILE(dataFn, modelFN, nFold, outcomeID, targetNodeId)
    dataResults = {'params': paramsJson, 'performance_meassures': perfMeassures_kFold}
    print(f"accuracy = {perfMeassures_kFold.get('accuracy')} for {nFold}-fold")
    print(f"confusion matrix = {perfMeassures_kFold.get('conMatrix')} for {nFold}-fold")
    print(f"dataset = {dataFn}")
    with open(jsonOutFN, 'w', encoding='utf-8') as outJSONFile:
        json.dump(dataResults, outJSONFile, indent=4)

    try:
        resultDS.write_file(jsonOutValidResultDSFN)
        # pysmile.learning.DataSet.write_file(jsonOutValidResultDSFN)
    except Exception as e:
        print(e)

    print(json.dumps(dataResults, indent=4))
    print('END')


if __name__ == '__main__':
    main()
