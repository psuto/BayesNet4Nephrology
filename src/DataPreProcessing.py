from abc import ABC, abstractclassmethod, abstractmethod


class DataPreProcessing(ABC):

    _processingVersion = "dbn_v01"

    @abstractmethod
    @property
    def processingVersion(self):
        return self._processingVersion

    @abstractmethod
    def preprocess(self,dataFrame):
        pass

    @abstractmethod
    def preprocessAndSave(self,dataFrame):
        pass

    @abstractmethod
    def saveToCSVFile(self, resultingDataFrames):
        pass