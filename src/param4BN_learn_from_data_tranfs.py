import collections
from math import isnan
from typing import Any, Union
import pandas as pd
import numpy as np
# from numpy.core._multiarray_umath import ndarray
# from pandas import Series
# from pandas.core.arrays import ExtensionArray
import sys
from datetime import datetime

# from pandas_log.patched_logs_functions import columns_added

# import buildBNStructure
import math
from tqdm import tqdm
import logging
import argparse



tqdm.pandas()

# Create a custom logger

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

console_log_level = logging.INFO  # default WARNING
file_log_level = logging.INFO  # default ERROR

logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(console_log_level)
f_handler.setLevel(file_log_level)
# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -% (message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

Interval2 = collections.namedtuple('Interval', 'lb ub')


class Interval:
    def __init__(self, lb, ub, lb_included=True, ub_included=True):
        self.lb = lb
        self.lb_included = lb_included
        self.ub = ub
        self.ub_included = ub_included

    def __str__(self):
        return f'Interval(lb={self.lb}, ub = {self.ub}, lb_included = {self.lb_included}, ub_included = {self.ub_included})'

    def __repr__(self):
        return f'Interval(lb={self.lb}, ub = {self.ub}, lb_included = {self.lb_included}, ub_included = {self.ub_included})'

    def __contains__(self, x):
        contains = False

        if isinstance(x, pd.Series):
            xdf = x  # pd.DataFrame(x)
            if self.lb_included:
                if self.ub_included:
                    contains = ((xdf >= self.lb) & (xdf <= self.ub))
                else:  # ub excluded
                    contains = ((xdf >= self.lb) & (xdf < self.ub))
            else:  # lb excluded
                if self.ub_included:
                    contains = ((xdf > self.lb) & (xdf <= self.ub))
                else:  # ub exclued
                    contains = ((xdf > self.lb) & (xdf < self.ub))
        else:
            if self.lb_included:
                if self.ub_included:
                    if self.lb <= x <= self.ub:
                        contains = True
                else:  # ub excluded
                    if self.lb <= x <= self.ub:
                        contains = True
                    if self.lb <= x < self.ub:
                        contains = True
            else:  # lb excluded
                if self.ub_included:
                    if self.lb < x <= self.ub:
                        contains = True
                else:  # ub exclued
                    if self.lb < x < self.ub:
                        contains = True
        return contains


todayVal = datetime.today()
timeStampStr = todayVal.strftime("%y-%m-%d_%H-%M-%S")

baselineKDIGOmol = {'black_male':
                        {Interval(16, 20): 133,
                         Interval(20, 24): 133,
                         Interval(25, 29): 133,
                         Interval(30, 39): 124,
                         Interval(40, 54): 115,
                         Interval(55, 65): 115,
                         Interval(65, 100): 106},

                    'other_male':
                        {Interval(16, 20): 115,
                         Interval(20, 24): 115,
                         Interval(25, 29): 106,
                         Interval(30, 39): 106,
                         Interval(40, 54): 97,
                         Interval(55, 65): 97,
                         Interval(65, 100): 88},
                    'black_female':
                        {Interval(16, 20): 106,
                         Interval(20, 24): 106,
                         Interval(25, 29): 97,
                         Interval(30, 39): 97,
                         Interval(40, 54): 88,
                         Interval(55, 65): 88,
                         Interval(65, 100): 80},
                    'other_female':
                        {Interval(16, 20): 88,
                         Interval(20, 24): 88,
                         Interval(25, 29): 88,
                         Interval(30, 39): 80,
                         Interval(40, 54): 80,
                         Interval(55, 65): 71,
                         Interval(65, 100): 71}
                    }

baselineKDIGOmg = {'black_male':
    {
        Interval(20, 24): 1.5,
        Interval(25, 29): 1.5,
        Interval(30, 39): 1.4,
        Interval(40, 54): 1.3,
        Interval(55, 65): 1.3,
        Interval(65, 100): 1.2},

    'other_male':
        {Interval(20, 24): 1.3,
         Interval(25, 29): 1.2,
         Interval(30, 39): 1.2,
         Interval(40, 54): 1.1,
         Interval(55, 65): 1.1,
         Interval(65, 100): 1.0},
    'black_female':
        {Interval(20, 24): 1.2,
         Interval(25, 29): 1.1,
         Interval(30, 39): 1.1,
         Interval(40, 54): 1.0,
         Interval(55, 65): 1.0,
         Interval(65, 100): 0.9},
    'other_female':
        {Interval(20, 24): 1.0,
         Interval(25, 29): 1.0,
         Interval(30, 39): 0.9,
         Interval(40, 54): 0.9,
         Interval(55, 65): 0.8,
         Interval(65, 100): 0.8}
}

ageIntervalsDict = baselineKDIGOmol['other_male']
ageIntervals = list(ageIntervalsDict.keys())


def convertCreatinineVals(c):
    mg_per_dL_2_micromol_per_L = 88.4017
    # print('Whole row')
    # print(c)
    res = c['creatinine_val_num']
    res2 = c['creatinine_val_units']
    # print(f'before {res},{res2}')
    if c['creatinine_val_units'] == 'mg/dL':
        res = c['creatinine_val_num'] * mg_per_dL_2_micromol_per_L
        res2 = c['creatinine_val_units'] = 'micro_mol/L'

    # print('after {res}, {res2}')
    return res  # [res,res2]


def addAge(df1):
    df1.loc[:, 'age_at_admit'] = pd.Series(dtype=pd.Int64Dtype)

    def calcAge(row):
        admtTime = row['admittime']
        dob = row['dob']
        diff = None
        try:
            diffYears = admtTime.year - dob.year
            diffMonths = admtTime.month - dob.month

            if True:
                if diffMonths < 0:
                    diffYears = diffYears - 1
                elif diffMonths == 0:
                    diffDays = admtTime.day - dob.day
                    if diffDays < 0:
                        diffYears = diffYears
            row['age_at_admit'] = diffYears
        except OverflowError as e:  # OverflowError:
            print(f'admtTime = {admtTime}')
            print(f'admtTime = {admtTime}')
            print(f'dob = {dob}')
            print(f'diff = {diff}')
            print(f'Error = {e} ')
            print(f'=========================================')

        # print(f'admtTime = {admtTime}, dob = {dob}, diff ={diff}')
        # print(f'===========================')
        return row

    tqdm.pandas(desc='Calc age')
    df1 = df1.progress_apply(lambda r: calcAge(r), axis=1)
    return df1


def getSCrBaseline4Age(age, x):
    res = math.nan
    for key, val in x.items():
        if age >= key.lb and age <= key.ub:
            # print(f'age = {age}, Scr baseline = {val}')
            res = val
            break
    if isnan(val):
        print('Stop')
    return val


def getBaselineSCr4Row(row, baselineKDIGOmol):
    age = row['age_at_admit']
    ethnicity = row['ethnicity']
    gender = row['gender']
    # ToDo: Fix ethnicity to BLACK AND OTHER INSTEAD WHITE AND OTHER
    keyGenderEthn = None
    if ethnicity == 'WHITE':
        if gender == 'M':
            keyGenderEthn = 'other_male'
        else:
            keyGenderEthn = 'other_female'
    else:
        if gender == 'M':
            keyGenderEthn = 'black_male'
        else:
            keyGenderEthn = 'black_female'

    subDict = baselineKDIGOmol.get(keyGenderEthn)
    baseline = getSCrBaseline4Age(age, subDict)
    return baseline


def addBaseline_02(df1):
    df1.loc[:, 'scr_baseline'] = pd.Series(dtype=int)
    c = df1.columns.to_list()
    for k, v in tqdm(baselineKDIGOmol.items(), desc='addBaseline_02 '):
        print(f'k = {k}, v= {v}')
        ethn, gen = k.upper().split('_')
        for ageInt, v2 in v.items():
            # print(f'k2 = {ageInt}')
            # print(f'v2 = {v2}')
            bEthnic = df1['ethnicity'] == ethn
            bGender = df1['gender'] == gen[0]
            bAge = ageInt.__contains__(df1['age_at_admit'])
            selectedMap = (bAge & bEthnic & bGender)
            # print(df1.loc[selectedMap, 'scr_baseline'])
            # print(f'Shape = {df1.loc[selectedMap, "scr_baseline"].shape}')
            # print(f'# row = {df1.loc[selectedMap, "scr_baseline"].shape[0]}')
            # print(f'# rows  = {df1.loc[selectedMap, "scr_baseline"].count()}')
            # print(f'# rows  = {len(df1.loc[selectedMap, "scr_baseline"].index)}')
            rowCount = df1[selectedMap].shape[0]
            if rowCount > 0:
                df1.loc[selectedMap, 'scr_baseline'] = v2
            else:
                print(f'No rows selected for:')
                print(f'ethn = {ethn}')
                print(f'gen = {gen}')
                print(f'age  = {ageInt}')
                print(f'v2 = {v2}')
                print()
            # print(df1['scr_baseline'].describe())
            print()
    print('addBaseline_02 finished!')
    return df1


def addBaseline_01(df1):
    dfRes = pd.DataFrame()
    df1.loc[:, 'scr_baseline'] = pd.Series(dtype=float)
    c = df1.columns.to_list()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()

    for subj in tqdm(unqueSubjID, desc=f'addBaseline_01 Baseline SCr for patients'):
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        tqdm.pandas(desc=f'Baseline SCr for patients {subj}')
        try:
            df2.loc[:, 'scr_baseline'] = df2.apply(lambda x: getBaselineSCr4Row(x, baselineKDIGOmol), axis=1)
        except Exception as e:
            print(e)
        dfRes = dfRes.append(df2)
    return dfRes


def addBaseline(df1):
    df1.loc[:, 'scr_baseline'] = pd.Series(dtype=float)
    groupedBySubj = df1.groupby('subject_id')
    for subjId, group in groupedBySubj:
        print(f'subjId = {subjId}')
        #     group['scr_baseline'] = group.apply(lambda r:getBaselineSCr4Row(r,baselineKDIGOmol), axis=1)
        tqdm.pandas(desc=f'baseline for subject {subjId}')
        group.loc[:, 'scr_baseline'] = group.progress_apply(lambda r: getBaselineSCr4Row(r, baselineKDIGOmol), axis=1)
        # group['scr_baseline']
    df100 = df1.merge(groupedBySubj)
    return df100


def akiDue2AbsIncrase48H(row, df):
    c = df.columns.to_list()
    labDate = row["labevent_charttime"]
    baselineSCr = row['scr_baseline']
    akiPresent = False
    lowerB_date = labDate - pd.DateOffset(hours=48)
    selected48HoursIdx = df['labevent_charttime'].between(lowerB_date, labDate)
    selected48Hours = df[selected48HoursIdx]
    numSelRows = len(selected48Hours)
    if numSelRows > 0:
        for i, r in selected48Hours.iterrows():
            try:
                scr_val_micromol = row['creatinine_val_num_mols']
            except:
                logger.debug(f'Some error in akiDue2AbsIncrase48H')
                print(f'Some error in akiDue2AbsIncrase48H')
            # Rule 1 difference in 48 hours
            try:
                scrDiff = scr_val_micromol - baselineSCr
                if (scrDiff) >= 26.5:
                    akiPresent = True
            except:
                e = sys.exc_info()[0]
                print(e)
        # raise NotImplemented()
    return akiPresent


def akiDue2RelIncrase7D(row, df):
    # for debugging
    c = df.columns.to_list()
    age = row['age_at_admit']
    ethnic = row['ethnicity']
    gender = row['gender']

    # =============================
    labDate = row["labevent_charttime"]
    baselineSCr = row['scr_baseline']
    akiPresent = False
    lowerB_date = labDate - pd.DateOffset(days=7)
    selected48HoursIdx = df['labevent_charttime'].between(lowerB_date, labDate)
    selected7Days = df[selected48HoursIdx]
    numSelRows = len(selected7Days)
    if numSelRows > 0:
        for i, r in selected7Days.iterrows():
            scr_val_micromol = row['creatinine_val_num_mols']
            # Rule 2 multiple in 7 days
            # if np.isnan(scr_val_micromol) | np.isnan(baselineSCr):
            #     akiPresent = False
            #     return akiPresent
            ratio = 0
            try:
                ratio = scr_val_micromol / baselineSCr
            except Exception as e:
                print(e)
            if ratio >= 1.5:
                akiPresent = True
                return akiPresent
    return akiPresent


def akiPresent(row, df):
    # ToDo: Complete
    akiPresent = False
    try:
        akiPresent = akiDue2AbsIncrase48H(row, df) | akiDue2RelIncrase7D(row, df)
    except Exception as e:
        print(f'row = {row}')
        print(e)
        print()
    return akiPresent


def addAKICol(df1, baselineKDIGOmol):
    """
    :param df1: dataframe
    :param baselineKDIGOmol: baseline values for SCr
    """
    df1.loc[:, 'AKI_present'] = pd.Series(dtype=bool)
    df1.loc[:, 'AKI_stage_1'] = pd.Series(dtype=bool)
    df1.loc[:, 'AKI_stage_2'] = pd.Series(dtype=bool)
    df1.loc[:, 'AKI_stage_3'] = pd.Series(dtype=bool)
    dfRes = pd.DataFrame()
    df1.loc[:, 'AKI_present'] = pd.Series(dtype=float)
    c = df1.columns.to_list()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    tqdm.pandas(desc='Adding AKI present')
    for subj in tqdm(unqueSubjID, desc='Adding AKI present'):
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        tqdm.pandas(desc=f'AKI present for subject {subj}')
        df2.loc[:, 'AKI_present'] = df2.apply(lambda r: akiPresent(r, df2), axis=1)
        dfRes = dfRes.append(df2)
    return dfRes


def addAKIinNext48H4Row(row, df):
    """

    :param row:
    :param df:
    :return:
    """
    c = df.columns.to_list()
    # =============================
    labDate = row["labevent_charttime"]
    upperB_date = labDate + pd.DateOffset(hours=48)
    selected48HoursIdx = df['labevent_charttime'].between(labDate, upperB_date)
    dfNext48H = df[selected48HoursIdx]
    numSelRows = len(dfNext48H)
    isAKIinNext48H = dfNext48H['AKI_present'].any()
    return isAKIinNext48H


def addAKIinNext48H(df1):
    """
    Adds label if there is AKI present in next 48 hours
    :param df1:
    :return:
    """
    dfRes = pd.DataFrame()
    df1['AKIinNext48H'] = pd.Series()  # pd.Series(dtype=float)
    c = df1.columns.to_list()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    for subj in unqueSubjID:
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        tqdm.pandas(desc=f'addAKIinNext48H {subj}')
        df2.loc[:, 'AKIinNext48H'] = df2.progress_apply(lambda r: addAKIinNext48H4Row(r, df2), axis=1)
        dfRes = dfRes.append(df2)
    return dfRes


def addDynamicScr(row, df, numPeriods, periodLenghtHours, scrCols):
    c = df.columns.to_list()
    # =============================
    labDate = row["labevent_charttime"]
    ub_date = labDate
    for col in scrCols:
        lowerB_date = ub_date - pd.DateOffset(hours=48) + pd.DateOffset(seconds=1)
        selected48HoursIdx = df['labevent_charttime'].between(lowerB_date, ub_date)
        dfPrev48H = df[selected48HoursIdx]
        numSelRows = len(dfPrev48H)
        scrMean = dfPrev48H['creatinine_val_num_mols'].mean()
        row[col] = scrMean
        # ==========================================
        ub_date = lowerB_date - pd.DateOffset(seconds=1)
    return row


def addDynamicScr0(row, df, numPeriods, periodLenghtHours, scrCols):
    c = df.columns.to_list()
    res = []
    # =============================
    labDate = row["labevent_charttime"]
    ub_date = labDate
    for i in range(0, numPeriods):
        lowerB_date = ub_date - pd.DateOffset(hours=48) + pd.DateOffset(seconds=1)
        selected48HoursIdx = df['labevent_charttime'].between(lowerB_date, ub_date)
        dfPrev48H = df[selected48HoursIdx]
        numSelRows = len(dfPrev48H)
        scrMean = dfPrev48H['creatinine_val_num_mols'].mean()
        res.append(scrMean)
        # ==========================================
        ub_date = lowerB_date - pd.DateOffset(seconds=1)
    series = pd.Series(res, index=scrCols)
    return series


def getDF4DBN(df1):
    """
    :param df1:
    :return:
    """
    dfxx = pd.DataFrame({'col_1': [0, 1, 2, 3], 'col_2': [4, 5, 6, 7]})
    # dfxx[['column_new_1', 'column_new_2', 'column_new_3']] = pd.DataFrame([[np.nan, 'dogs',3]], index=dfxx.index)
    dfxx[['column_new_1', 'column_new_2', 'column_new_3']] = pd.DataFrame([[np.nan] * 3], index=dfxx.index)

    numPeriods = 4
    periodLenghtHours = 48
    scrCols = ["Scr_level"]
    scrCols.extend(["Scr_level_" + str(x) for x in range(1, numPeriods)])
    df1[scrCols] = pd.DataFrame([[np.nan] * len(scrCols)], index=df1.index)
    dfRes = pd.DataFrame(columns=scrCols)
    print('=======================================')
    # df1['AKIinNext48H'] = pd.Series() # pd.Series(dtype=float)
    c = df1.columns.to_list()
    # # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    print('=======================================')
    # numPeriods, periodLenghtHours
    print('=======================================')
    for subj in tqdm(unqueSubjID, desc=f'4 periods of SCr for patient ({getDF4DBN})'):
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        df2 = df2.apply(lambda r: addDynamicScr(r, df2, numPeriods, periodLenghtHours, scrCols), axis=1)
        # df2 = df2.apply(lambda r: addDynamicScr(r, df2, numPeriods, periodLenghtHours, scrCols), axis=1)
        dfRes = dfRes.append(df2)
    return dfRes


def discretizeSCrSingleVal(x, scrStatesAndIntervals):
    """
    For single value

    :param x:
    :param scrStatesAndIntervals:
    :return:
    """
    itms = scrStatesAndIntervals.items()
    res = None
    for k, v in scrStatesAndIntervals.items():
        if x in v:
            res = k
            return res
    # Check if value is none
    if math.isnan(x):
        res = ""  # "(none)"
        return res
    firstState = list(scrStatesAndIntervals.keys())[0]
    firstInt = scrStatesAndIntervals[firstState]
    lastState = list(scrStatesAndIntervals.keys())[-1]
    lastInterval = scrStatesAndIntervals[lastState]
    if x < firstInt.lb:
        res = firstState
    if x > lastInterval.ub:
        res = lastState
    return res


def discretizeSCrSingleCol(sScr, scrStatesAndIntervals):
    """
    Discretization for single column

    :param sScr:
    :param scrStatesAndIntervals:
    :return:
    """
    tqdm.pandas(desc=f'Discretize SCr values')
    newSeries = sScr.progress_apply(lambda v: discretizeSCrSingleVal(v, scrStatesAndIntervals))
    return newSeries


def discretizeSCrVals4MultiCols(sScr, scrStatesAndIntervals):
    # newSeries = sScr.apply(lambda r: discretizeSCrVal(r,scrStatesAndIntervals))
    tqdm.pandas(desc=f'Discretize scr values multiCols')
    newSeries = sScr.progress_apply(lambda r: discretizeSCrSingleCol(r, scrStatesAndIntervals))
    return newSeries


scrIntervals = [
    Interval(0, 10, ub_included=False), Interval(10, 20, ub_included=False), Interval(20, 30, ub_included=False),
    Interval(30, 40, ub_included=False), Interval(40, 50, ub_included=False), Interval(50, 60, ub_included=False),
    Interval(60, 70, ub_included=False), Interval(70, 80, ub_included=False), Interval(80, 90, ub_included=False),
    Interval(90, 100, ub_included=False), Interval(100, 110, ub_included=False),
    Interval(110, 120, ub_included=False),
    Interval(120, 130, ub_included=False), Interval(130, 140, ub_included=False),
    Interval(140, 150, ub_included=False),
    Interval(150, 160, ub_included=False), Interval(160, 170, ub_included=False),
    Interval(170, 180, ub_included=False),
    Interval(180, 600, ub_included=False)
]

scrStates = {f'V{i.lb}_{i.ub}': i for i in scrIntervals}  # 'V00_10': Interval(0, 10)

ageIntervalsDict = [
    Interval(16, 19), Interval(20, 24), Interval(25, 29), Interval(30, 39), Interval(40, 54), Interval(55, 65),
    Interval(66, 200)
]

ageStates = {i: f'Y{i.lb}_{i.ub}' for i in ageIntervalsDict}  # 'V00_10': Interval(0, 10)

# AKI_in next 48 hours
aki48H_states = [True, False]
genderStates = ["M", "F"]


def transformEthnicity4Model(df):
    bBlack = df['ethnicity'].str.lower() == 'black'
    bOther = ~bBlack
    print(f"before transform ethnicity = {df['ethnicity'].unique()}")
    df.loc[bBlack, 'ethnicity'] = 'BLACK'
    df.loc[bOther, 'ethnicity'] = 'OTHER'
    print(f"after transform ethnicity = {df['ethnicity'].unique()}")
    return df


def discretizeAge(dfOutL, ageStates):
    dfOutL.rename(columns={'Age': 'AgeInt'}, inplace=True)
    dfOutL['Age'] = pd.Series()
    for interval, state in tqdm(ageStates.items(), desc='Discretizing Age'):
        ageMap = ((dfOutL['AgeInt'] >= interval.lb) & (dfOutL['AgeInt'] <= interval.ub))
        dfOutL.loc[ageMap, 'Age'] = state
    return dfOutL


def main():
    nRows2REad = params.numRows
    print(f'Number rows = {nRows2REad}')
    dataFileN = '../../data/AKI_data_200325_full_dob_v02.csv'
    # df1 = pd.read_csv('../../data/AKI_data_200304_full.csv', nrows=nRows2REad)
    df1 = readData(dataFileN, nRows2REad)
    nRowsIn = len(df1)
    df1.drop('hadm_id', axis=1, inplace=True)
    tqdm.pandas(desc=f'convertCreatinineVals to micoromols per litre')
    df1.loc[:, 'creatinine_val_num_mols'] = df1.progress_apply(convertCreatinineVals, axis=1)
    print(df1.columns.to_list())
    print(df1.dtypes)
    # print(df1['creatinine_val_num_mols'].head())
    print('----------------------------------------------')
    df1.loc[:, 'admittime'] = pd.to_datetime(df1['admittime'])
    df1.loc[:, 'deathtime'] = pd.to_datetime(df1['deathtime'])
    df1.loc[:, 'labevent_charttime'] = pd.to_datetime(df1['labevent_charttime'])
    df1.loc[:, 'dob'] = pd.to_datetime(df1['dob'])
    # print(df1[['admittime', 'dob']].head())
    print('----------------------------------------------')
    df1 = df1.sort_values(by=['subject_id', 'admisssion_hadm_id', 'admittime', 'labevent_charttime'])
    df1 = addAge(df1)
    print(df1['age_at_admit'])
    print('----------------------------------------------')
    # df1 = addBaseline_01(df1)
    cols = df1.columns.to_list()
    print(cols)
    print(f' "age_at_admit" in df = {"age_at_admit" in df1}')
    print(f' "gender" in df = {"gender" in df1}')
    print(f' "ethnicity" in df = {"ethnicity" in df1}')
    print('===========================')
    print(df1['age_at_admit'].describe())
    print(df1['gender'].describe())
    print(df1['ethnicity'].describe())
    print('===========================')
    print(f'Distinct values of "age_at_admit": {df1["age_at_admit"].unique().tolist()}')
    print(f'Distinct values of ethnicity: {df1["ethnicity"].unique().tolist()}')
    print(f'Distinct values of "gender": {df1["gender"].unique().tolist()}')
    print('===========================')
    df1 = transformEthnicity4Model(df1)
    df1 = addBaseline_02(df1)
    # df100 = addBaseline_01(df1)
    # List of node names to learn: 'Gender' , 'Age' , 'AKI48H' , 'Scr_level'
    df1 = addAKICol(df1, baselineKDIGOmol)
    print(df1.columns.to_list())
    # print(df1.head())
    print('AKI_present')
    # print(df1['AKI_present'].head())
    df1 = addAKIinNext48H(df1)
    # print(df1.head())
    dfOut = getDF4DBN(df1)
    cNames = dfOut.columns.to_list()
    # ['Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3', 'subject_id', 'admisssion_hadm_id',
    # 'labevent_charttime', 'creatinine_val', 'creatinine_val_num', 'creatinine_val_units', 'is_creatinine_value_normal',
    # 'diagnosis_seq_num', 'diagnosis_icd9_code', 'diagnosis_long_title', 'admission_diagnosis', 'gender', 'ethnicity',
    # 'admittime', 'deathtime', 'dob', 'creatinine_val_num_mols', 'age_at_admit', 'scr_baseline', 'AKI_present',
    # 'AKI_stage_1', 'AKI_stage_2', 'AKI_stage_3', 'AKIinNext48H']
    #  SCR levels
    dynamicSCRs = ['Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3']

    # dfOut['SCr_num_mols_discr'] = discretizeSCrVals(dfOut['creatinine_val_num_mols'],scrStates)
    # select column
    translateColnNames = {'gender': 'Gender', 'age_at_admit': 'Age', 'AKIinNext48H': 'AKI48H', 'Scr_level': 'Scr_level',
                          'Scr_level_1': 'Scr_level_1', 'Scr_level_2': 'Scr_level_2', 'Scr_level_3': 'Scr_level_3'}
    oldSelectedColName = list(translateColnNames.keys())
    newSelectedColName = list(translateColnNames.values())
    # dfOutWONaN.rename(columns=translateColnNames, inplace=True  dfOut.rename(columns=translateColnNames, inplace=True)
    dfOut.rename(columns=translateColnNames, inplace=True)
    tqdm.pandas(desc='adding AKI48')
    dfOut.loc[:, 'AKI48H'] = dfOut['AKI48H'].progress_apply(lambda x: convertBooleanToString(x))
    dfOutBackup = dfOut
    dfOut = dfOut[newSelectedColName]
    dfOutWONaN = dfOut.dropna()
    dfOut.loc[:, dynamicSCRs] = discretizeSCrVals4MultiCols(dfOut[dynamicSCRs], scrStates)
    dfOutWONaN.loc[:, dynamicSCRs] = discretizeSCrVals4MultiCols(dfOutWONaN[dynamicSCRs], scrStates)

    cols3 = dfOut.columns.to_list()
    print(cols3)
    # print(dfOut.head(3))
    # List of node names to learn: 'Gender' , 'Age' , 'AKI48H' , 'Scr_level'
    # Cols ot keep: 'gender' -  'Gender' | 'age_at_admit' - 'Age' |    'AKIinNext48H' - 'AKI48H' | 'SCr_num_mols_discr' - 'Scr_level'

    dfOut = discretizeAge(dfOut, ageStates)
    outDF2 = dfOut[newSelectedColName]
    dfOutWONaN = discretizeAge(dfOutWONaN, ageStates)
    dfOutWONaN = dfOutWONaN[newSelectedColName]

    # df1 = pd.read_csv('../../data/AKI_data_200325_full_dob_v02.csv', nrows=500)
    fnOut_woNADated = f'../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA_ri_{nRows2REad}_ri2_{nRowsIn}_ro_{len(dfOutWONaN)}_{timeStampStr}.csv'
    fnOut_wNADated = f'../../data/AKI_data_200325_full_dob_v02_forBN_w_NA_ri_{nRows2REad}_ri2_{nRowsIn}_ro_{len(outDF2)}_{timeStampStr}.csv'
    # fnOut_woNA = f'../../data/AKI_data_200325_full_dob_v02_forBN_wo_NA.csv'
    # fnOut_wNA = f'../../data/AKI_data_200325_full_dob_v02_forBN_w_NA.csv'
    # outDF2.to_csv(fnOut_wNA, index=False)
    outDF2.to_csv(fnOut_wNADated, index=False)
    # dfOutWONaN.to_csv(fnOut_woNA, index=False)
    dfOutWONaN.to_csv(fnOut_woNADated, index=False)
    print('----------------------------------------------')
    # All cols
    # ['Scr_level', 'Scr_level_1', 'Scr_level_2', 'Scr_level_3', 'subject_id', 'admisssion_hadm_id', 'labevent_charttime',
    # 'creatinine_val', 'creatinine_val_num', 'creatinine_val_units', 'is_creatinine_value_normal', 'diagnosis_seq_num',
    # 'diagnosis_icd9_code', 'diagnosis_long_title', 'admission_diagnosis', 'gender', 'ethnicity', 'admittime', 'deathtime',
    # 'dob', 'creatinine_val_num_mols', 'age_at_admit', 'scr_baseline', 'AKI_present', 'AKI_stage_1', 'AKI_stage_2',
    # 'AKI_stage_3', 'AKIinNext48H', 'SCr_num_mols_discr']
    print('----------------------------------------------')
    print('---       FINISHED     -')
    print('----------------------------------------------')


def readData(dataFileN, nRows2REad):
    df1 = pd.DataFrame()
    if nRows2REad <= 0:
        df1 = pd.read_csv(dataFileN)
    else:
        df1 = pd.read_csv(dataFileN, nrows=nRows2REad)
    return df1


def convertBooleanToString(x):
    x = 'TRUE' if x else 'FALSE'
    return x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple")
    parser.add_argument("-n", action="store", dest="numRows", type=int, default=0,
                        help="number of rows to read")

    params = parser.parse_args()  # ['--fSimul="oooooooooooooooooo"'],'--fWF="xxxxxxxxxxxxxxxxxxxx"'
    print(params)
    main()
