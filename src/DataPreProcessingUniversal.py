import argparse
import pathlib

import pandas as pd
from tqdm import tqdm
import numpy as np

from DataPreProcessing import DataPreProcessing
from DataPreProcessing4BNV01 import DataPreProcessing4BNv01, ResultingDF
from DataPreprocessingContext import DataPreprocessingContext, InputFileVersionInfo
from DataPreprocessingMethods import DataPreprocessingMethods
import param4BN_learn_from_data_tranfs as pp
from collections import namedtuple


def addDynamicScr(row, df1, numPeriods, periodLenghtHours):
    """
    Sort it into two numPeriods periods

    :param r:
    :type r:
    :param df2:
    :type df2:
    :param numPeriods:
    :type numPeriods:
    :param periodLenghtHours:
    :type periodLenghtHours:
    :param scrCols:
    :type scrCols:
    :return:
    :rtype:
    """
    pass
    colNames = list(df1.columns)
    df2 = pd.DataFrame(columns=colNames)
    # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
    # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
    # 'diagnosis_long_title', 'admission_diagnosis', 'gender', 'ethnicity', 'admittime', 'deathtime', 'dob',
    # 'creatinine_val_num_mols', 'age_at_admit', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2',
    # 'AKI_stage_3', 'toBeIncuded', 'AKIinNext48H', 'Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3']
    dfN = pd.DataFrame([row] * numPeriods)
    dfN['Time_Period'] = range(1, 5)
    newScRCol = 'ScR4Period'
    dfN[newScRCol] = 0
    labDate = row["labevent_charttime"]
    ub_date = labDate
    newScRColVals = []
    for lIndex, lRow in dfN.iterrows():
        lowerB_date = ub_date - pd.DateOffset(hours=periodLenghtHours) + pd.DateOffset(seconds=1)
        selected48HoursIdx = df1['labevent_charttime'].between(lowerB_date, ub_date)
        dfPrev48H = df1[selected48HoursIdx]
        numSelRows = len(dfPrev48H)
        scrMean = dfPrev48H['creatinine_val_num_mols'].mean()
        newScRColVals.append(scrMean)
        # ==========================================
        ub_date = lowerB_date - pd.DateOffset(seconds=1)
        pass
    dfN[newScRCol] = newScRColVals
    return dfN


class DataPreProcessing4GP00(DataPreProcessing4BNv01, DataPreprocessingMethods):
    # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
    # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
    # 'diagnosis_long_title', 'admission_diagnosis', 'Gender', 'ethnicity', 'admittime', 'deathtime', 'dob',
    # 'creatinine_val_num_mols', 'Age', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2', 'AKI_stage_3',
    # 'toBeIncuded', 'AKI48H', 'Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3', 'Time_Period', 'ScR4Period']
    # ===============================================================================================================
    #  ['Gender', 'Age', 'AKI48H', 'Scr_level', 'Time_Period', 'ScR4Period']
    translateColnNames = {
                            'subject_id':"id", 'gender': 'Gender', 'age_at_admit': 'Age', 'AKIinNext48H': 'AKI48H', 'Scr_level': 'Scr_level',
                             'Time_Period':'Time_Period', 'ScR4Period':'ScR4Period'

                          }

    newSelectedColName = [
        'id', 'Gender', 'Age', 'AKI48H', 'Time_Period', 'ScR4Period'
    ]


    def preprocess(self, dataFrame):
        """
        Calculates ScR values per 4 periods (parametrized)  each as average over 48 hours (parametrized)
        """
        df1 = dataFrame
        df1 = dataFrame
        df1.drop('hadm_id', axis=1, inplace=True)
        tqdm.pandas(desc=f'convertCreatinineVals to micoromols per litre')
        df1.loc[:, 'creatinine_val_num_mols'] = df1.progress_apply(pp.convertCreatinineVals, axis=1)
        df1 = self.convertColumns2DateTime(df1)
        df1 = df1.sort_values(by=['subject_id', 'admisssion_hadm_id', 'admittime', 'labevent_charttime'])
        df1 = pp.addAge(df1)
        df1 = pp.transformEthnicity4Model(df1)
        df1 = pp.addBaseline_02(df1)
        # ToDo Add Forward and Back2ward approach for AKI48H labeling
        df1 = pp.addAKICol(df1, pp.baselineKDIGOmol)
        df1 = pp.excludeRecWPreviousAKI(df1)
        df1 = pp.addAKIinNext48H(df1)
        df1 = self.scrVals4GP(df1)
        # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
        # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
        # 'diagnosis_long_title', 'admission_diagnosis', 'gender', 'ethnicity', 'admittime', 'deathtime', 'dob',
        # 'creatinine_val_num_mols', 'age_at_admit', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2',
        # 'AKI_stage_3', 'toBeIncuded', 'AKIinNext48H']
        # df1 = pp.getDF4DBN(df1)
        df1.rename(columns=self.translateColnNames, inplace=True)
        tqdm.pandas(desc='adding AKI48')
        # df1.loc[:, 'AKI48H'] = df1['AKI48H'].progress_apply(lambda x: pp.convertBooleanToString(x))

        # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
        # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
        # 'diagnosis_long_title', 'admission_diagnosis', 'Gender', 'ethnicity', 'admittime', 'deathtime', 'dob',
        # 'creatinine_val_num_mols', 'Age', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2', 'AKI_stage_3',
        # 'toBeIncuded', 'AKI48H', 'Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3', 'Time_Period', 'ScR4Period']
        #==============================================================================================
        # ['Gender', 'Age', 'AKI48H', 'Scr_level', 'Time_Period', 'ScR4Period']
        #==============================================================================================
        # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
        # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
        # 'diagnosis_long_title', 'admission_diagnosis', 'Gender', 'ethnicity', 'admittime', 'deathtime',
        # 'dob', 'creatinine_val_num_mols', 'Age', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2',
        # 'AKI_stage_3', 'toBeIncuded', 'AKI48H', 'Time_Period', 'ScR4Period']
        # =================================================================
        # ['Gender', 'Age', 'AKI48H', 'Scr_level', 'Time_Period', 'ScR4Period']
        # =================================================================
        # ['subject_id', 'admisssion_hadm_id', 'labevent_charttime', 'creatinine_val', 'creatinine_val_num',
        # 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num', 'diagnosis_icd9_code',
        # 'diagnosis_long_title', 'admission_diagnosis', 'Gender', 'ethnicity', 'admittime', 'deathtime', 'dob',
        # 'creatinine_val_num_mols', 'Age', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2',
        # 'AKI_stage_3', 'toBeIncuded', 'AKI48H', 'Time_Period', 'ScR4Period']

        df1 = df1[self.newSelectedColName]
        df1WONaN = df1.dropna()
        result = ResultingDF(df1, df1WONaN)
        return result


    @staticmethod
    def scrVals4GP(df1: pd.DataFrame):
        """

        :param df1:
        :type df1:
        :return:
        :rtype:
        """
        numPeriods = 4
        periodLenghtHours = 48
        # scrCols = ["Scr_level"]
        # scrCols.extend(["Scr_level_" + str(x) for x in range(1, numPeriods)])
        # df1[scrCols] = pd.DataFrame([[np.nan] * len(scrCols)], index=df1.index)
        # dfRes = pd.DataFrame(columns=scrCols)
        print('=======================================')
        # df1['AKIinNext48H'] = pd.Series() # pd.Series(dtype=float)
        c = df1.columns.to_list()
        # # subjIDUnique = df1[]
        unqueSubjID = df1.subject_id.unique()
        print('=======================================')
        # numPeriods, periodLenghtHours
        print('=======================================')
        patID = "None"
        dfN: pd.DataFrame = pd.DataFrame()
        for subj in tqdm(unqueSubjID, desc=f'4 periods of SCr for previouse patient {patID} scrVals4GP'):
            patID = subj
            map1 = df1['subject_id'] == subj
            df2: pd.DataFrame = df1[map1]
            for index, row in df2.iterrows():
                dfNTmp = addDynamicScr(row, df2, numPeriods, periodLenghtHours)
                dfN = pd.concat([dfN, dfNTmp], ignore_index=True)
        return dfN

    def preprocessAndSave(self, dataFrame):
        pass

    def saveToCSVFile(self, resultingDataFrames,nRows2REad,inputFileVersionInfo:InputFileVersionInfo,outputDirPath):
        fnOut_woNADated = f'{self._processingVersion}_{inputFileVersionInfo.versionString}_ri_'\
                          f'{nRows2REad}_ro_{len(resultingDataFrames.dfWoNA)}'\
                          f'_{self._processingVersion}_woNA_D_{pp.timeStampStr}.csv'
        fnOut_wNADated = f'{self._processingVersion}_{inputFileVersionInfo.versionString}_ri_'\
                          f'{nRows2REad}_ro_{len(resultingDataFrames.dfWoNA)}'\
                          f'_{self._processingVersion}_wNA_D_{pp.timeStampStr}.csv'
        # outputDirPath
        fnOut_woNADated = outputDirPath / fnOut_woNADated
        fnOut_wNADated =  outputDirPath / fnOut_wNADated


        print(f"Writing output for df without NA to {fnOut_woNADated}")
        print(f"Writing output for df with NA to {fnOut_wNADated}")
        df:pd.DataFrame = resultingDataFrames.df
        df.to_csv(fnOut_wNADated, index=False)
        resultingDataFrames.dfWoNA.to_csv(fnOut_woNADated, index=False)


    def __init__(self):
        super(DataPreProcessing4BNv01, self).__init__()
        self._processingVersion = 'Ph2_GP_V00'


    @property
    def nRows2Read(self):
        return self._nRows2Read

    @property
    def processingVersion(self):
        return self._processingVersion


if __name__ == "__main__":
    def main():
        nRows2REad = params.numRows
        dataFileN = params.inputDataSetFile
        preProcessorName = params.preprocessorID
        dataProcessor = None
        if preProcessorName == 'Ph2_GP_V00':
            dataProcessor = DataPreProcessing4GP00()
        dataPreprocessingContext = DataPreprocessingContext(dataFileN, nRows2REad, dataProcessor)
        dataPreprocessingContext.setDataPreProcessor(dataProcessor)
        results = dataPreprocessingContext.preprocess()
        dataPreprocessingContext.saveToCSVFile(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("-n", action="store", dest="numRows", type=int, default=-1,
                        help="number of rows to read")

    parser.add_argument("--fds", action="store", dest="inputDataSetFile", type=str,
                        default='../../data/AKI_data_200325_full_dob_v02_test.csv',
                        help="file path to file with csv dataset file (default = '../../data/AKI_data_200325_full_dob_v02_test.csv')")

    parser.add_argument("--ppId", action="store", dest="preprocessorID", type=str, default='Ph2_GP_V00',
                        help="Preprocessor ID: BNv01 = for BN with excluding record if AKI present previosly in past 4 weeks")

    params = parser.parse_args()  #
    print("*****************************")
    print("Input parameters:")
    print(params)
    print("*****************************")
    main()
