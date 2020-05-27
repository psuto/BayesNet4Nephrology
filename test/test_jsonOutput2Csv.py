import pytest
import jsonOutput2Csv
import pandas as pd


def test_add_data():
    colNames = ['a']
    inputDir = r'..\output\paramsAndREsults_20-05-08_00-14-30.json'
    df = pd.DataFrame(columns=['bnVersion', 'numTimeSteps', 'orderAutoregression', 'targetNode', 'outcomeID', 'accuracy', 'tp', 'fp', 'fn', 'tn', 'sensitivity', 'specificity', 'accuracy_calc', 'precision', 'prevalence', 'tpr', 'fpr', 'fnr', 'tnr', 'model_file_name'])
    df = jsonOutput2Csv.addData(df, inputDir)
    print()
    # >>> print p.search('no class at all')
    # <_sre.SRE_Match object at 0x...>
    # >>> print p.search('the declassified algorithm')
    # None
    # >>> print p.search('one subclass is')
    print()
