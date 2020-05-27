import re
import typing as tp




def ectractInfoFromModelFileName1(baseFN):
    """

    :param baseFN:
    :type baseFN:
    :return:
    :rtype:
    """
    p = re.compile(r'^BN(\d{1,3})_.*Drug_v(\d{1,3}).*_(\d{1,3})timeSteps_(\d{1,3})\w{0,3}_order.*', re.IGNORECASE)
    m = p.match(baseFN)
    vVersionStr = "-1"
    bnVersionStr = "-1"
    numTimeStepsStr = "-1"
    orderAutoregressionStr = "-1"
    matched = False
    if m:
        orderAutoregressionStr = m.group(4)
        numTimeStepsStr = m.group(3)
        vVersionStr = m.group(2)
        bnVersionStr = m.group(1)
        matched = True
    return matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr


def ectractInfoFromModelFileName2(baseFN):
    """

    :param baseFN:
    :type baseFN:
    :return:
    :rtype:
    """
    # 'AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl'
    print()
    p = re.compile(r'.*_.*Drug_v(\d{1,3})_order(\d{1,3})_(\d{1,3})_training\.xdsl$', re.IGNORECASE)
    m = p.match(baseFN)
    vVersionStr = "-1"
    bnVersionStr = "-1"
    numTimeStepsStr = "-1"
    orderAutoregressionStr = "-1"
    matched = False
    if m:
        # orderAutoregressionStr = m.group(3)
        numTimeStepsStr = m.group(3)
        # vVersionStr = m.group(1)
        # bnVersionStr = "-1"
        matched = True
    return matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr


def ectractInfoFromModelFileName3(baseFN: str):
    """

    :param baseFN:
    :type baseFN:
    :return:
    :rtype:
    """
    print()
    # 'AKI prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_3rd_order_training.xdsl'
    p = re.compile(r'.*_.*Drug_v(\d{1,3})_(\d{1,3})timeSteps_(\d{1,3})\w{1,3}_order_.*', re.IGNORECASE)
    m = p.match(baseFN)
    vVersionStr = "-1"
    bnVersionStr = "-1"
    numTimeStepsStr = "-1"
    orderAutoregressionStr = "-1"
    matched = False
    if m:
        # print(f"g0 = {m.group(0)}, g1 = {m.group(1)}, g2 = {m.group(2)}, g3 = {m.group(3)}")
        orderAutoregressionStr = m.group(3)
        numTimeStepsStr = m.group(2)
        vVersionStr = m.group(1)
        bnVersionStr = "-1"
        matched = True
    return matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr

def extractInfoFromModelFileNameGeneral(modelfileName):
    matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName1(
        modelfileName)
    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName2(
            modelfileName)
    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromModelFileName3(
            modelfileName)

    if not matched:
        matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr = ectractInfoFromResultsFName4(
            modelfileName)

    orderAutoregression = -1
    bnVersion = -1
    numTimeSteps = -1
    modelName = "BN"

    try:
        orderAutoregression = int(orderAutoregressionStr)
        bnVersion = int(bnVersionStr)
        numTimeSteps = int(numTimeStepsStr)
        vVersion = int(vVersionStr)
        modelName = f"BN{bnVersion:02d}"
    except Exception as e:
        print(e)
    # ToDo: Add modelName everywhere
    print()
    result = (matched,modelName, bnVersion, numTimeSteps, orderAutoregression, vVersion)
    return result


def ectractInfoFromResultsFName4(baseFN):
    """

    :param baseFN:
    :type baseFN:
    :return:
    :rtype:
    """
    print()
    # 'AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_trained.xdsl'
    p = re.compile(r'.*Drug_v(\d{1,3})_order(\d{1,3})_trained.*', re.IGNORECASE)
    m = p.match(baseFN)
    vVersionStr = "-1"
    bnVersionStr = "-1"
    numTimeStepsStr = "-1"
    orderAutoregressionStr = "-1"
    matched = False
    if m:
        # print(f"g0 = {m.group(0)}, g1 = {m.group(1)}, g2 = {m.group(2)}, g3 = {m.group(3)}")
        orderAutoregressionStr = m.group(2)
        numTimeStepsStr = m.group(1)
        matched = True
    return matched, bnVersionStr, numTimeStepsStr, orderAutoregressionStr, vVersionStr