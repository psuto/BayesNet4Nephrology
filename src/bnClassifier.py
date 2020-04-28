from sklearn.base import BaseEstimator, ClassifierMixin

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
from param4BN_learn_from_data_tranfs import readData


class BayesianNetworkClassifier(BaseEstimator, ClassifierMixin):
    """
    Bayesian network classifier.
    """

    def __init__(self, bayesNetFile):
        """
        Called when initializing the classifier
        """
        self.bayesNetFile = bayesNetFile
        net = pysmile.Network()
        self.bayesNet = net.read_file(bayesNetFile)

    def change_evidence_and_update(self, net, node_id, outcome_id):

        if outcome_id is not None:

            net.set_evidence(node_id, outcome_id)

        else:

            net.clear_evidence(node_id)

        net.update_beliefs()

        self.print_all_posteriors(net)

        print("")

    def fit(self, X, y=None):
        dfAll = pd.concat([X, y], axis=1)
        tmpFileName = '../../data/tmpDataFit.csv'
        dfAll.to_csv(tmpFileName, index=False, header=True)
        print()
        ds = pysmile.learning.DataSet()
        ds.read_file(tmpFileName)

        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()
        em.learn(ds, self.net, matching)
        # ds.add_int_variable()
        # ds.set_state_names()
        # ds.set_missing()
        return self


def main():
    nrows = 2000
    bayesNetFile = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl"
    bnC = BayesianNetworkClassifier(bayesNetFile)
    dataWONanFN = '../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    dataWONaN = readData(dataWONanFN, nrows)
    cols1 = dataWONaN.columns.to_list()
    print(cols1)
    targetColName = 'AKI48H'
    y = pd.DataFrame(dataWONaN.pop(targetColName))
    x = dataWONaN
    # ds = pysmile.learning.DataSet()
    # ds.read_file("mydatafile.txt")
    bnC.fit(x, y)
    print(f'')


if __name__ == '__main__':
    main()
