from param4BN_learn_from_data_tranfs import readData


class DataPreprocessingContext():
    def __init__(self,dataFileName, nRows2Read, dataPreProcessor):
        self._dataFrame =  readData(dataFileName, nRows2Read)# dataframe
        self._dataFileName = dataFileName
        self.nRows2Read = nRows2Read


    def setDataPreProcessor(self, dataPreProcessor):
        self.dataPreProcessor = dataPreProcessor


    def preprocess(self):
        results = self.dataPreProcessor.preprocess(self._dataFrame)
        return results