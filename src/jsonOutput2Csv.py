import json
from pathlib import Path
import os
import pandas as pd
import re
import param4BN_learn_from_data_tranfs as parBN
from utilities import ectractInfoFromModelFileName1, ectractInfoFromModelFileName2, ectractInfoFromModelFileName3, \
    ectractInfoFromResultsFName4


def calcRelConfMatrix(confusionMatrix):
    tp = confusionMatrix[0][0]
    fp = confusionMatrix[0][1]
    fn = confusionMatrix[1][0]
    tn = confusionMatrix[1][1]
    sumRecords = sum(map(sum, confusionMatrix))
    print()

    # rConfusionMatrix = [element/sumRecords for element in enumerate(sublist) for sublist in confusionMatrix]
    n = len(confusionMatrix)
    rConfusionMatrix = [[j / sumRecords for j in i] for i in confusionMatrix]
    # print()
    return rConfusionMatrix


def calcPerfMetrics(confusionMatrix):
    tp = confusionMatrix[0][0]
    fp = confusionMatrix[0][1]
    fn = confusionMatrix[1][0]
    tn = confusionMatrix[1][1]
    sumRecords = sum(map(sum, confusionMatrix))
    print()
    condPositive = tp + fn  # N
    condNegative = tn + fp  # N
    sensitivity = tp / condPositive  # TPR, recall, hit reate
    specificity = tn / condNegative  # TNR
    accuracy_calc = (tp + tn) / (condPositive + condNegative)
    # ======================
    prevalence = condPositive / sumRecords
    # ======================
    precision = tp / (tp + fp)  # positive predictive value
    neg_predictive_val = tn / (tn + fn)
    tpr = tp / condPositive  # sensitivity recall
    fpr = fp / condNegative  # fall-out
    fnr = fn / condPositive  # miss rate
    tnr = tn / condNegative  # specificity
    f1_score = 2 * (precision * sensitivity) / (precision + sensitivity)
    results = {'sensitivity': sensitivity, 'specificity': specificity, 'accuracy_calc': accuracy_calc,
               'precision': precision, 'prevalence': prevalence, 'tpr': tpr, 'fpr': fpr, 'fnr': fnr, 'tnr': tnr}
    print()
    return results


def isWithMissingData(fileName):
    # 'AKI_data_200325_full_dob_v02_forBN_w_NA_20-04-14_15-13-35.csv'
    p = re.compile(r'.*_(\w{1,2})_NA_.*', re.IGNORECASE)
    m = p.match(fileName)
    flagStr = m.group(1)
    flagWOmissing = None
    if flagStr == "w":
        flagWOmissing=True
    else:
        flagWOmissing=False
    return flagWOmissing




def addData(df, filePath):
    """

    :param df:
    :param name:
    :return:
    """
    with open(filePath) as f:
        jsonData = json.load(f)

    # ====================================================
    # === params
    # =====================================================
    # params
    # {'nFold': 5, 'targetNodeId': 'AKI48H', 'outcomeID': 0, 'inputFile': 'C:\\Work\\dev\\dECMT_src\\data\\AKI_data_200325_full_dob_v02_forBN_w_NA_ri_0_ri2_217148_ro_217148_20-04-24_23-30-27.csv', 'modelFN': '../models/BN03_AKI_prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl'}
    params = jsonData.get('params')
    targetNode = params.get('targetNodeId')
    outcomeID = params.get('outcomeID')
    nFold = params.get('nFold')
    outcomeID = params.get('outcomeID')
    targetNodeId = params.get('targetNodeId')
    modelFN = params.get('modelFN')
    inputFilePath = params.get('inputFile')
    import ntpath
    inputFile = ntpath.basename(inputFilePath)
    dataFwMissing = isWithMissingData(inputFile)
    baseFN = ntpath.basename(modelFN)
    # ================================
    # performance_meassures
    # {'accuracy': 0.7789233791748527, 'conMatrix': [[49559, 14066], [10674, 142849]], 'timeOfCrossValidation_sec': 178548.47850227356, 'timeOfCVstr': '2 days, 1:35:48.478502', 'recordCount': 217148, 'outcomeID': 0}
    # =========================
    performance_meassures = jsonData.get('performance_meassures')
    accuracy = performance_meassures.get('accuracy')
    confusionMatrix = performance_meassures.get('conMatrix')
    # 'recordCount'
    recordCount = performance_meassures.get('recordCount')
    relConfMatrix = calcRelConfMatrix(confusionMatrix)
    perfMetrics = calcPerfMetrics(confusionMatrix)
    #  'BN03_AKI_prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl'
    # p = re.compile(r'^BN(\d{1,3})_.*Drug_v(\d{1,3}).*_(\d{1,3})timeSteps_(\d{1,3})\w{1,2}_order.*', re.IGNORECASE)
    matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName1(
        baseFN)
    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName2(
            baseFN)
    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName3(
            baseFN)

    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromResultsFName4(
            baseFN)

    if matched:
        orderAutoregression = -1
        bnVersion = -1
        numTimeSteps = -1
        modelName = "BN"

        try:
            orderAutoregression = int(orderAutoregressionStr)
            bnVersion = int(bnVersionStr)
            numTimeSteps = int(numTimeStepsStr)
            vVersion = int(vVersionStr)
            modelName = f"BN{bnVersion:02d}"
        except Exception as e:
            print(e)
        print()
        print()
        # df columns: model_file_name
        # {'accuracy': 0.7789233791748527, 'conMatrix': [[49559, 14066], [10674, 142849]], 'timeOfCrossValidation_sec': 178548.47850227356, 'timeOfCVstr': '2 days, 1:35:48.478502', 'recordCount': 217148, 'outcomeID': 0}
        columns: {
            'modelName',
            'bnVersion',
            'numTimeSteps',
            'orderAutoregression',
            'targetNode',
            'outcomeID',
            'missing_data',
            'accuracy',
            'tp',
            'fp',
            'fn',
            'tn',
            'nFold',
            'inputFile',
            'model_file_name'}

        row = {
            'bnVersion': bnVersion,
            'numTimeSteps': numTimeSteps,
            'orderAutoregression': orderAutoregression,
            'targetNode': targetNode,
            'outcomeID': outcomeID,
            'recordCount': recordCount,
            'accuracy': accuracy,
            'tp': confusionMatrix[0][0],
            'fp': confusionMatrix[0][1],
            'fn': confusionMatrix[1][0],
            'tn': confusionMatrix[1][1]
        }
        # {'sensitivity': 0.8227881725964172, 'specificity': 0.9103591116209413, 'accuracy_calc': 0, 'precision': 0.7789233791748527, 'prevalence': 0.27738224620995816, 'tpr': 0.8227881725964172, 'fpr': 0.08964088837905873, 'fnr': 0.17721182740358277, 'tnr': 0.17721182740358277}
        row.update(perfMetrics)
        row.update({'model_file_name': baseFN, 'nFold': nFold, 'recordCount': recordCount, 'inputFile': inputFile,
                    'missing_data':dataFwMissing, 'modelName':modelName})
        df = df.append(row, ignore_index=True)
        colNames = list(row.keys())
    else:
        print(f"Skipping file \"{baseFN}\"")
    print(f"DataFrame: df.head()")
    print(df.head())
    return df


def main():
    print(f"Current directory {os.getcwd()}")
    colNames = ['a', 'b']
    # df = pd.DataFrame(columns=colNames)
    df = pd.DataFrame(
        columns=['modelName','bnVersion', 'numTimeSteps', 'orderAutoregression', 'targetNode', 'outcomeID', 'nFold', 'recordCount',
                 'accuracy', 'tp', 'fp', 'fn', 'tn', 'sensitivity', 'specificity', 'accuracy_calc',
                 'precision', 'prevalence', 'tpr', 'fpr', 'fnr', 'tnr', 'model_file_name'])
    # 'model_file_name': baseFN,'nFold':nFold,'recordCount':recordCount
    inputDir = r'..\output'
    # inputDir = r'..\output\test00'
    p = Path(inputDir)
    for name in p.glob('*.json'):
        print(name)
        print()
        df = addData(df, name)
    output_name = f"sumary_metrics_v00_time_time={parBN.timeStampStr}.csv"
    outputCSV = Path(inputDir) / output_name
    # Todo:  200524 filter only with version >= 0
    df.to_csv(outputCSV, index=False)
    print("Finishe calculations!!!")


if __name__ == '__main__':
    main()
