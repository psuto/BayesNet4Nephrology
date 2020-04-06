import collections
from typing import Any, Union
import pandas as pd
import numpy as np
from numpy.core._multiarray_umath import ndarray
from pandas import Series
from pandas.core.arrays import ExtensionArray
import sys

import buildBNStructure


Interval = collections.namedtuple('Interval', 'lb ub')




baselineKDIGOmol = {'black_male':
                        {Interval(20, 24): 133,
                         Interval(25, 29): 133,
                         Interval(30, 39): 124,
                         Interval(40, 54): 115,
                         Interval(55, 65): 115,
                         Interval(65, 100): 106},

                    'other_male':
                        {Interval(20, 24): 115,
                         Interval(25, 29): 106,
                         Interval(30, 39): 106,
                         Interval(40, 54): 97,
                         Interval(55, 65): 97,
                         Interval(65, 100): 88},
                    'black_female':
                        {Interval(20, 24): 106,
                         Interval(25, 29): 97,
                         Interval(30, 39): 97,
                         Interval(40, 54): 88,
                         Interval(55, 65): 88,
                         Interval(65, 100): 80},
                    'other_female':
                        {Interval(20, 24): 88,
                         Interval(25, 29): 88,
                         Interval(30, 39): 80,
                         Interval(40, 54): 80,
                         Interval(55, 65): 71,
                         Interval(65, 100): 71}
                    }

baselineKDIGOmg = {'black_male':
                       {Interval(20, 24): 1.5,
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
    df1['age_at_admit'] = pd.Series(dtype=pd.Int64Dtype)

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

    df1 = df1.apply(lambda r: calcAge(r), axis=1)
    return df1



def getSCrBaseline4Age(age,x):
    for key, val in x.items():
        if age>=key.lb and age<=key.ub:
            # print(f'age = {age}, Scr baseline = {val}')
            return val


def getBaselineSCr4Row(row, baselineKDIGOmol):
    age = row['age_at_admit']
    ethnicity = row['ethnicity']
    gender = row['gender']
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

def addBaseline_01(df1):
    dfRes = pd.DataFrame()
    df1['scr_baseline'] = pd.Series(dtype=float)
    c = df1.columns.to_list()
    print()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    for subj in unqueSubjID:
        map1 = df1['subject_id']==subj
        df2 = df1[map1]
        df2['scr_baseline'] = df2.apply(lambda x: getBaselineSCr4Row(x,baselineKDIGOmol),axis=1)
        dfRes = dfRes.append(df2)
        print()

    # groupedBySubj = df1.groupby('subject_id')
    # xxx = groupedBySubj['creatinine_val_num_mols']
    #
    # dfres = groupedBySubj['creatinine_val_num_mols'].tranform(lambda x: getBaselineSCr4Row(x,baselineKDIGOmol))
    return dfRes


def addBaseline(df1):
    df1['scr_baseline'] = pd.Series(dtype=float)
    groupedBySubj = df1.groupby('subject_id')
    for subjId, group in groupedBySubj:
        print(f'subjId = {subjId}')
        #     group['scr_baseline'] = group.apply(lambda r:getBaselineSCr4Row(r,baselineKDIGOmol), axis=1)
        group['scr_baseline'] = group.apply(lambda r: getBaselineSCr4Row(r, baselineKDIGOmol), axis=1)
        # group['scr_baseline']
    df100 = df1.merge(groupedBySubj)
    return df100


def akiDue2AbsIncrase48H(row, df):
    c = df.columns.to_list()
    labDate = row["labevent_charttime"]
    baselineSCr = row['scr_baseline']
    akiPresent = False
    lowerB_date = labDate-pd.DateOffset(hours=48)
    selected48HoursIdx = df['labevent_charttime'].between(lowerB_date,labDate)
    selected48Hours = df[selected48HoursIdx]
    numSelRows = len(selected48Hours)
    if numSelRows>0:
        for i,r in selected48Hours.iterrows():
            scr_val_micromol = row['creatinine_val_num_mols']
            # Rule 1 difference in 48 hours
            try:
                scrDiff = scr_val_micromol - baselineSCr
                if (scrDiff)>=26.5:
                    akiPresent = True
            except:
                e = sys.exc_info()[0]
                print(e)
                print()
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
    lowerB_date = labDate-pd.DateOffset(days=7)
    selected48HoursIdx = df['labevent_charttime'].between(lowerB_date,labDate)
    selected7Days = df[selected48HoursIdx]
    numSelRows = len(selected7Days)
    if numSelRows>0:
        for i,r in selected7Days.iterrows():
            scr_val_micromol = row['creatinine_val_num_mols']
            # Rule 2 multiple in 7 days
            ratio = scr_val_micromol/baselineSCr
            if ratio >= 1.5:
                akiPresent = True
                return akiPresent
            print()

    return akiPresent


def akiPresent( row,df):
    akiPresent = akiDue2AbsIncrase48H(row , df) |  akiDue2RelIncrase7D(row , df)
    return akiPresent



def addAKICol(df1,baselineKDIGOmol):
    """
    :param df1: dataframe
    :param baselineKDIGOmol: baseline values for SCr
    """
    df1['AKI_present'] = pd.Series()
    df1['AKI_stage_1'] = pd.Series()
    df1['AKI_stage_2'] = pd.Series()
    df1['AKI_stage_3'] = pd.Series()
    dfRes = pd.DataFrame()
    df1['AKI_present'] = pd.Series(dtype=float)
    c = df1.columns.to_list()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    print()
    for subj in unqueSubjID:
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        df2['AKI_present'] = df2.apply(lambda r: akiPresent(r, df2), axis=1)
        dfRes = dfRes.append(df2)
        print()
    print()
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
    upperB_date = labDate+pd.DateOffset(hours=48)
    selected48HoursIdx = df['labevent_charttime'].between(labDate, upperB_date)
    dfNext48H = df[selected48HoursIdx]
    numSelRows = len(dfNext48H)
    isAKIinNext48H = dfNext48H['AKI_present'].any()
    print()
    return isAKIinNext48H

def addAKIinNext48H(df1):
    """
    :param df1:
    :return:
    """
    dfRes = pd.DataFrame()
    df1['AKIinNext48H'] = pd.Series() # pd.Series(dtype=float)
    c = df1.columns.to_list()
    # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    print()
    for subj in unqueSubjID:
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        df2['AKIinNext48H'] = df2.apply(lambda r: addAKIinNext48H4Row(r, df2), axis=1)
        dfRes = dfRes.append(df2)
        print()
    print()
    return dfRes


def addDynamicScr(row, df, numPeriods, periodLenghtHours, scrCols):
    c = df.columns.to_list()
    res = []
    # =============================
    labDate = row["labevent_charttime"]
    ub_date = labDate

    for i in range(0,numPeriods):
        lowerB_date = ub_date - pd.DateOffset(hours=48)+pd.DateOffset(seconds=1)
        selected48HoursIdx = df['labevent_charttime'].between(lowerB_date, ub_date)
        dfPrev48H = df[selected48HoursIdx]
        numSelRows = len(dfPrev48H)
        scrMean = dfPrev48H['creatinine_val_num_mols'].mean()
        res.append(scrMean)
        # ==========================================
        print()
        ub_date= lowerB_date-pd.DateOffset(seconds=1)
    return pd.Series(res)

def getDF4DBN(df1):
    """
    :param df1:
    :return:
    """
    numPeriods = 4
    periodLenghtHours = 48
    scrCols = ["Scr_level"]
    scrCols.extend(["Scr_level_"+str(x) for x in range(1,numPeriods)])
    dfRes = pd.DataFrame(columns=scrCols)
    print('=======================================')
    # df1['AKIinNext48H'] = pd.Series() # pd.Series(dtype=float)
    c = df1.columns.to_list()
    # # subjIDUnique = df1[]
    unqueSubjID = df1.subject_id.unique()
    print('=======================================')
    # numPeriods, periodLenghtHours
    print('=======================================')
    print()
    for subj in unqueSubjID:
        map1 = df1['subject_id'] == subj
        df2 = df1[map1]
        df2[scrCols] = df2.apply(lambda r: addDynamicScr(r, df2,numPeriods,periodLenghtHours, scrCols), axis=1)
        dfRes = dfRes.append(df2)
        print()
    # print()
    return dfRes


def main():
    # df1 = pd.read_csv('../../data/AKI_data_200304_full.csv', nrows=20)
    df1 = pd.read_csv('../../data/AKI_data_200325_full_dob_v02.csv', nrows=500)
    df1.drop('hadm_id', axis=1, inplace=True)

    df1['creatinine_val_num_mols'] = df1.apply(convertCreatinineVals, axis=1)
    print(df1.columns.to_list())
    print(df1.dtypes)
    print(df1['creatinine_val_num_mols'].head())
    print('----------------------------------------------')
    df1['admittime'] = pd.to_datetime(df1['admittime'])
    df1['deathtime'] = pd.to_datetime(df1['deathtime'])
    df1['labevent_charttime'] = pd.to_datetime(df1['labevent_charttime'])
    df1['dob'] = pd.to_datetime(df1['dob'])
    print(df1[['admittime', 'dob']].head())
    print('----------------------------------------------')
    df1 = df1.sort_values(by=['subject_id', 'admisssion_hadm_id', 'admittime', 'labevent_charttime'])
    df1 = addAge(df1)
    print(df1['age_at_admit'])
    print('----------------------------------------------')
    df1 = addBaseline_01(df1)
    # df100 = addBaseline_01(df1)
    df1 = addAKICol(df1,baselineKDIGOmol)
    print(df1.columns.to_list())
    print(df1.head())
    print('AKI_present')
    print(df1['AKI_present'].head())
    df1 = addAKIinNext48H(df1)
    print(df1.head())
    dfOut = getDF4DBN(df1)
    print('----------------------------------------------')
    print('----------------------------------------------')
    print('----------------------------------------------')





if __name__ == '__main__':
    main()
