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
import argparse
import datetime as dt


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
    print(f'{nFold}-fold CV started at {time.strftime("%H:%M %y-%m-%d")}')
    validator.k_fold(em, nFold)
    deltaT = time.time() - t0
    time4CVstr = str(dt.timedelta(seconds=deltaT))
    print(f'Finished {nFold}-fold crossvalidation with SMILE in {deltaT} seconds')
    logger.debug(f'Finished {nFold}-fold crossvalidation with SMILE in {deltaT} seconds')
    acc = validator.get_accuracy(targetClassNodehandle, outcomeID)
    confMatrix = validator.get_confusion_matrix(targetNodeId)
    resultDS = validator.get_result_data_set()
    return ({'accuracy': acc, 'conMatrix': confMatrix, 'timeOfCrossValidation_sec': deltaT, "timeOfCVstr": time4CVstr, 'recordCount': recordCount,
             'outcomeID': outcomeID}, resultDS)
    pysmile.learning.DataSet

def main():
    modelFN = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl"
    modelFN = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl"
    modelFN = params.inputModelFile
    # dataFn = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    # dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_w_NA_20-04-14_14-35-01.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_20-04-14_14-35-01.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_20-04-14_15-13-35.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_w_NA_20-04-14_15-13-35.csv"
    dataFn = "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_ri_0_ri2_217148_ro_93120_20-04-24_23-30-27_short.csv"
    dataFn = params.inputDataSetFile
    outcomeID = params.outcomeIdx
    nFold = params.nFold #5  # 10
    targetNodeId = params.targetNodeId
    jsonOutFN = f'..\output\paramsAndREsults_{parBN.timeStampStr}.json'
    jsonOutValidResultDSFN = f'..\output\validator_dsResults_{parBN.timeStampStr}.json'
    paramsJson = {'nFold': nFold, 'targetNodeId': "AKI48H", 'outcomeID': outcomeID, 'inputFile': dataFn,
                  'modelFN': modelFN}
    print(json.dumps(paramsJson, indent=4))
    perfMeassures_kFold, resultDS = validateWithSMILE(dataFn, modelFN, nFold, outcomeID, targetNodeId)
    dataResults = {'params': paramsJson, 'performance_meassures': perfMeassures_kFold}
    print(f"accuracy = {perfMeassures_kFold.get('accuracy')} for {nFold}-fold")
    print(f"confusion matrix = {perfMeassures_kFold.get('conMatrix')} for {nFold}-fold")
    print(f"dataset = {dataFn}")
    with open(jsonOutFN, 'w', encoding='utf-8') as outJSONFile:
        json.dump(dataResults, outJSONFile, indent=4)

    try:
        print(f"Writing to jsonOutValidResultDSFN")
        resultDS.write_file(jsonOutValidResultDSFN)
        print(f"Written to jsonOutValidResultDSFN")
        # pysmile.learning.DataSet.write_file(jsonOutValidResultDSFN)
    except Exception as e:
        print(e)

    print(json.dumps(dataResults, indent=4))
    print('END')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("--fm", action="store", dest="inputModelFile", type=str,
                        default="../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03.xdsl",
                        help="file path to file with xdsl model (default = '../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03.xdsl')")
    parser.add_argument("--fds", action="store", dest="inputDataSetFile", type=str, default="xxxxxxxxxx",
                        help="file path to file with csv dataset file (default = 'C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_ri_0_ri2_217148_ro_93120_20-04-24_23-30-27_short.csv')")
    # targetNodeId = "AKI48H"
    parser.add_argument("--tnode", action="store", dest="targetNodeId", type=str, default="AKI48H",
                        help="Name of the target node (default = 'AKI48H')")
    parser.add_argument("--outcidx", action="store", dest="outcomeIdx", type=int, default=0,
                        help="Outcome index in target node.")
    parser.add_argument("--nfold", action="store", dest="nFold", type=int, default=5,
                        help="# fold in crossvalidation n>0")
    # outcomeID
    params = parser.parse_args()  # ['--fSimul="oooooooooooooooooo"'],'--fWF="xxxxxxxxxxxxxxxxxxxx"'
    print(params)
    # import     datetime as dt
    # td = dt.timedelta(seconds=3684)
    # print(str(td))
    # sleep(52)
    main()
