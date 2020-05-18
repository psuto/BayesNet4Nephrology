import json
from pathlib import Path
import os
import pandas as pd
from pandas.tests.indexing.conftest import numeric_indexing_engine_type_and_dtype


def relConfMatrix(confusionMatrix):
    tp = confusionMatrix[1, 1]
    fp = confusionMatrix[1, 2]
    fn = confusionMatrix[2, 1]
    tn = confusionMatrix[2, 2]
    



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
    import ntpath
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
    relConfMatrix = relConfMatrix(confusionMatrix)
    import re
    #  'BN03_AKI_prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl'
    p = re.compile(r'^BN(\d{1,3})_.*Drug_v(\d{1,3}).*_(\d{1,3})timeSteps_(\d{1,3})\w{1,2}_order.*', re.IGNORECASE)
    m = p.match(baseFN)
    if m:
        orderAutoregressionStr = m.group(4)
        numTimeStepsStr = m.group(3)
        vVersionStr = m.group(2)
        bnVersionStr = m.group(1)

        orderAutoregression = -1
        bnVersion = -1
        numTimeSteps = -1
        vVersion = -1
        try:
            orderAutoregression = int(orderAutoregressionStr)
            bnVersion = int(bnVersionStr)
            numTimeSteps = int(numTimeStepsStr)
            vVersion = int(vVersionStr)
        except Exception as e:
            print(e)
        print()
        print()
        # df columns: model_file_name
        # {'accuracy': 0.7789233791748527, 'conMatrix': [[49559, 14066], [10674, 142849]], 'timeOfCrossValidation_sec': 178548.47850227356, 'timeOfCVstr': '2 days, 1:35:48.478502', 'recordCount': 217148, 'outcomeID': 0}

        columns: {
            'bnVersion',
            'numTimeSteps',
            'orderAutoregression',
            'targetNode',
            'outcomeID',
            'accuracy',
            'tp',
            'fp',
            'fn',
            'tn',
            'model_file_name'}

        row = {
            'bnVersion': bnVersion,
            'numTimeSteps': numTimeSteps,
            'orderAutoregression': orderAutoregression,
            'targetNode': targetNode,
            'outcomeID': outcomeID,
            'accuracy': accuracy,
            'tp': performance_meassures[1, 1],
            'fp': performance_meassures[1, 2],
            'fn': performance_meassures[2, 1],
            'tn': performance_meassures[2,2]



            'model_file_name': baseFN

        }
        df.append(row,ignore_index=True)
    return df


def main():
    print(f"Current directory {os.getcwd()}")
    colNames = ['a', 'b']
    df = pd.DataFrame(columns=colNames)
    inputDir = r'..\output'
    p = Path(inputDir)
    for name in p.glob('*.json'):
        print(name)
        print()
        addData(df, name)


if __name__ == '__main__':
    main()
