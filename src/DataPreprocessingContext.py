import pathlib

from DataPreProcessing import DataPreProcessing
from param4BN_learn_from_data_tranfs import readData
import re
from collections import namedtuple


class FileNameParser():
    def parsePhase1FileName4Version(fileName):
        pass


def extractPhase1Version(dataFileName):
    # '../../data/AKI_data_200325_full_dob_v02_test.csv'
    # '../../data/AKI_nephro_ph1_v00_s00_test.csv'
    '../../data/ph1_mimicAKI_v00_s00_test.csv'
    p = re.compile('(ph1_(\w*)_(v(\d{1,2})))_(s(\d{1,2}))_(.*)\.csv$')
    m = p.match("ph1_mimicAKI_v00_s00_test.csv")
    matches = m.groups()
    # ('ph1_mimicAKI_v00', 'mimicAKI', 'v00', '00', 's00', '00', 'test')
    res = {"versionString":m[1],"dataSetStr":m[2],"dataVersionStr":m[3],"dataVersion":m[4],"seriesStr":m[5],"seriesNumber":m[6],"annotation":m[7]}
    return res

InputFileVersionInfo =   namedtuple("InputFileVersionInfo","versionString dataSetStr dataVersionStr dataVersion seriesStr seriesNumber annotation")

class DataPreprocessingContext():
    def __init__(self, dataFileName, nRows2Read, dataPreProcessor: DataPreProcessing):
        df = readData(dataFileName, nRows2Read)  # dataframe
        df = df[df["subject_id"].notna()]
        purePath = pathlib.PurePath(dataFileName)
        parentDir2 = purePath.parent.parent
        # path.name
        '../../data_all/BN_nephro-onco_MIMIC_data/ph1_mimicAKI_v00_s00_test.csv'
        outputPath = pathlib.Path(parentDir2) / "BN_nephro-onco_MIMIC_data_output"
        pathlib.Path.mkdir(outputPath,exist_ok=True)
        self._dataFrame = df
        self.extractInfoFromInputFileName(dataFileName, nRows2Read)
        self._outputDirPath = outputPath
        # =================================================

    def extractInfoFromInputFileName(self, dataFileName, nRows2Read):
        strNameMatches = extractPhase1Version(dataFileName)
        # {'versionString': 'ph1_mimicAKI_v00', 'dataSetStr': 'mimicAKI', 'dataVersionStr': 'v00', 'dataVersion': '00', 'seriesStr': 's00', 'seriesNumber': '00'}
        self._phase1Version = strNameMatches["versionString"]
        self._seriesString = strNameMatches["seriesStr"]
        self._inFileAnnotaion = strNameMatches["annotation"]
        self._dataFileName = dataFileName
        self._nRows2Read = nRows2Read
        inputFileVersionInfo = InputFileVersionInfo(strNameMatches["versionString"], strNameMatches["dataSetStr"],
                                                    strNameMatches["dataVersionStr"], strNameMatches["dataVersion"],
                                                    strNameMatches["seriesStr"], strNameMatches["seriesNumber"],
                                                    strNameMatches["annotation"])
        self._inputFileVersionInfo = inputFileVersionInfo
    @property
    def outputDirPath(self):
        return self._outputDirPath

    @property
    def inputFileVersionInfo(self):
        self._inputFileVersionInfo

    @property
    def dataFileName(self):
        return self._dataFileName

    @property
    def inFileAnnotaion(self):
        return self._inFileAnnotaion

    @property
    def seriesString(self):
        return self._seriesString

    @property
    def phase1Version(self):
        return self._phase1Version

    def setDataPreProcessor(self, dataPreProcessor):
        self.dataPreProcessor: DataPreProcessing = dataPreProcessor

    def preprocess(self):
        results = self.dataPreProcessor.preprocess(self._dataFrame)
        return results

    def saveToCSVFile(self, results):
        self.dataPreProcessor.saveToCSVFile(results, self._nRows2Read,self._inputFileVersionInfo,self._outputDirPath)
        pass
