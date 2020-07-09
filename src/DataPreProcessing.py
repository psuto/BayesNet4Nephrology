from abc import ABC, abstractclassmethod, abstractmethod


class DataPreProcessing(ABC):

    _processingVersion = "dbn_v01"

    @property
    @abstractmethod
    def nRows2Read(self):
        pass

    @property
    @abstractmethod
    def processingVersion(self):
        pass

    @abstractmethod
    def preprocess(self,dataFrame):
        raise NotImplementedError
        pass

    @abstractmethod
    def preprocessAndSave(self,dataFrame):
        pass

    @abstractmethod
    def saveToCSVFile(self, resultingDataFrames,nRows2Read,inputFileInfoStr):
        pass