import argparse
from builtins import print

import param4BN_learn_from_data_tranfs as pp
import pandas as pd

from DataPreProcessing import DataPreProcessing
from DataPreprocessingContext import DataPreprocessingContext
from param4BN_learn_from_data_tranfs import tqdm, addAge, transformEthnicity4Model, addBaseline_02, \
    baselineKDIGOmol, addAKICol, excludeRecWPreviousAKI
from collections import namedtuple

ResultingDF = namedtuple('ResultingDFs', 'df dfWoNA')


def preprocessData():
    df = pd.DataFrame


class DataPreProcessing4BNv01(DataPreProcessing):

    def __init__(self):
        # self._processingVersion =  "BN_v01"
        self._processingVersion = "Ph2_BN_V00"

    @staticmethod
    def processingVersion(self):
        return self._processingVersion


    def saveToCSVFile(self, resultingDataFrames, nRows2REad):
        def saveToCSVFile(self, resultingDataFrames, nRows2REad, inputFileVersionInfo: InputFileVersionInfo,
                          outputDirPath):
            fnOut_woNADated = f'{self._processingVersion}_{inputFileVersionInfo.versionString}_ri_' \
                              f'{nRows2REad}_ro_{len(resultingDataFrames.dfWoNA)}' \
                              f'_{self._processingVersion}_woNA_D_{pp.timeStampStr}.csv'
            fnOut_wNADated = f'{self._processingVersion}_{inputFileVersionInfo.versionString}_ri_' \
                             f'{nRows2REad}_ro_{len(resultingDataFrames.dfWoNA)}' \
                             f'_{self._processingVersion}_wNA_D_{pp.timeStampStr}.csv'
            # outputDirPath
            fnOut_woNADated = outputDirPath / fnOut_woNADated
            fnOut_wNADated = outputDirPath / fnOut_wNADated

            print(f"Writing output for df without NA to {fnOut_woNADated}")
            print(f"Writing output for df with NA to {fnOut_wNADated}")
            df: pd.DataFrame = resultingDataFrames.df
            df.to_csv(fnOut_wNADated, index=False)
            resultingDataFrames.dfWoNA.to_csv(fnOut_woNADated, index=False)

    @property
    def nRows2Read(self):
        return self._nRows2Read


    def preprocessAndSave(self, dataFrame):
        res = preprocessData()
        df = res.get("")
        dfWoNA = res.get("")

    # @property
    # def processingVersion(self):
    #     return self._processingVersion

    def preprocess(self, dataFrame):
        """ transformations applied to raw data """
        df1 = dataFrame
        df1.drop('hadm_id', axis=1, inplace=True)
        tqdm.pandas(desc=f'convertCreatinineVals to micoromols per litre')
        df1.loc[:, 'creatinine_val_num_mols'] = df1.progress_apply(pp.convertCreatinineVals, axis=1)
        df1 = self.convertColumns2DateTime(df1)
        df1 = df1.sort_values(by=['subject_id', 'admisssion_hadm_id', 'admittime', 'labevent_charttime'])
        df1 = addAge(df1)
        df1 = transformEthnicity4Model(df1)
        df1 = addBaseline_02(df1)
        df1 = addAKICol(df1, baselineKDIGOmol)
        df1 = excludeRecWPreviousAKI(df1)
        df1 = pp.addAKIinNext48H(df1)
        df1 = pp.getDF4DBN(df1)
        df1.rename(columns=pp.translateColnNames, inplace=True)
        tqdm.pandas(desc='adding AKI48')
        df1.loc[:, 'AKI48H'] = df1['AKI48H'].progress_apply(lambda x: pp.convertBooleanToString(x))
        df1WONaN = df1.dropna()
        df1.loc[:, pp.dynamicSCRs] = pp.discretizeSCrVals4MultiCols(df1[pp.dynamicSCRs], pp.scrStates)
        df1WONaN.loc[:, pp.dynamicSCRs] = pp.discretizeSCrVals4MultiCols(df1WONaN[pp.dynamicSCRs], pp.scrStates)

        df1 = pp.discretizeAge(df1, df1 = df1[pp.newSelectedColName])

        df1WONaN = pp.discretizeAge(df1WONaN, pp.ageStates)
        df1WONaN = df1WONaN[pp.newSelectedColName]
        result = ResultingDF(df1, df1WONaN)
        return result

    def convertColumns2DateTime(self, df1):
        df1 = self.convetStringToDateTime(df1, 'admittime')
        df1 = self.convetStringToDateTime(df1, 'deathtime')
        df1 = self.convetStringToDateTime(df1, 'labevent_charttime')
        df1 = self.convetStringToDateTime(df1, 'dob')
        return df1

    def convetStringToDateTime(self, df1, colName):
        df1.loc[:, colName] = pd.to_datetime(df1[colName])
        return df1


def main():
    # Todo: Extract info from input data to see versio of 'raw' data
    dataFileN = '../../data/AKI_data_200325_full_dob_v02.csv'
    dataFileN = '../../data/AKI_data_200325_full_dob_v02_test.csv'
    # df1 = pd.read_csv('../../data/AKI_data_200304_full.csv', nrows=nRows2REad)
    nRows2REad = params.numRows
    dataFileN = params.inputDataSetFile
    preProcessorName = params.preprocessorID
    dataProcessor = None
    if preProcessorName == "Ph2_BN_V00":
        dataProcessor = DataPreProcessing4BNv01()
    if dataProcessor is not None:
        dataPreprocessingContext = DataPreprocessingContext(dataFileN, nRows2REad, dataProcessor)
        dataPreprocessingContext.setDataPreProcessor(dataProcessor)
        results = dataPreprocessingContext.preprocess()
        dataPreprocessingContext.saveToCSVFile(results)

    print(f"Finished with dataProcessor {'OK' if (dataProcessor is not None) else  'None'}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("-n", action="store", dest="numRows", type=int, default=2000,
                        help="number of rows to read")

    parser.add_argument("--fds", action="store", dest="inputDataSetFile", type=str,
                        default='../../data/AKI_data_200325_full_dob_v02_test.csv',
                        help="file path to file with csv dataset file (default = '../../data/AKI_data_200325_full_dob_v02_test.csv')")
    # Todo: 200704 class version String from Class
    parser.add_argument("--ppId", action="store", dest="preprocessorID", type=str, default='BNv01',
                        help="Preprocessor ID: BNv01 = for BN with excluding record if AKI present previosly in past 4 weeks")

    params = parser.parse_args()  #
    print("*****************************")
    print("Input parameters:")
    print(params)
    print("*****************************")
    main()
