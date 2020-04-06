# import param4BN_learn_from_data_tranfs
import pysmile
# pysmile_license is your license key
import pysmile_license
import collections
from typing import Any, Union
import pandas as pd
import numpy as np
from numpy.core._multiarray_umath import ndarray
from pandas import Series
from pandas.core.arrays import ExtensionArray
import sys


class BNManipulation():
    def __init__(self):
        pass

    def print_cpt_matrix(self, net, node_handle):
        cpt = net.get_node_definition(node_handle)
        parents = net.get_parents(node_handle)
        dim_count = 1 + len(parents)

        dim_sizes = [0] * dim_count
        for i in range(0, dim_count - 1):
            dim_sizes[i] = net.get_outcome_count(parents[i])
        dim_sizes[len(dim_sizes) - 1] = net.get_outcome_count(node_handle)

        coords = [0] * dim_count
        for elem_idx in range(0, len(cpt)):
            bnManipulation.index_to_coords(elem_idx, dim_sizes, coords)

            outcome = net.get_outcome_id(node_handle, coords[dim_count - 1])
            out_str = "    P(" + outcome

            if dim_count > 1:
                out_str += " | "
                for parent_idx in range(0, len(parents)):
                    if parent_idx > 0:
                        out_str += ","
                    parent_handle = parents[parent_idx]
                    out_str += net.get_node_id(parent_handle) + "=" + \
                               net.get_outcome_id(parent_handle, coords[parent_idx])

            prob = cpt[elem_idx]
            out_str += ")=" + str(prob)
            print(out_str)

    def index_to_coords( self,index, dim_sizes, coords):
        """
        # Turns list of parameters into 2-D array
        :param index:
        :param dim_sizes:
        :param coords:
        """
        prod = 1
        len_dim_sizes = len(dim_sizes)
        range_dim_sizes = range(len_dim_sizes - 1, -1, -1)
        for i in range_dim_sizes:
            coords[i] = int(index / prod) % dim_sizes[i]
            prod *= dim_sizes[i]

bnManipulation = BNManipulation()





class Interval:
    def __init__(self,lb,ub,lb_included=True,ub_included=True):
        self.lb=lb
        self.lb_included=lb_included
        self.ub = ub
        self.ub_included = ub_included

    def __contains__(self,x):
        contains = False
        if self.lb_included:
            if self.ub_included:
                if self.lb<=x<=self.ub:
                    contains=True
            else: # ub excluded
                if self.lb<=x<=self.ub:
                    contains=True
                if self.lb<=x<self.ub:
                    contains=True
        else:# lb excluded
            if self.ub_included:
                if self.lb<x<=self.ub:
                    contains=True
            else:# ub exclued
                if self.lb<x<self.ub:
                    contains=True
        return contains


def main():
    scrIntervals = [
                    Interval(0, 10,ub_included=False), Interval(10, 20, ub_included=False), Interval(20, 30,ub_included=False),
                    Interval(30, 40,ub_included=False), Interval(40, 50,ub_included=False), Interval(50, 60,ub_included=False),
                    Interval(60, 70,ub_included=False), Interval(70, 80,ub_included=False), Interval(80, 90,ub_included=False),
                    Interval(90, 100,ub_included=False), Interval(100, 110,ub_included=False), Interval(110, 120,ub_included=False),
                    Interval(120, 130,ub_included=False), Interval(130, 140,ub_included=False), Interval(140, 150,ub_included=False),
                    Interval(150, 160,ub_included=False), Interval(160, 170,ub_included=False), Interval(170, 180,ub_included=False),
                    Interval(180, 400,ub_included=False)
                    ]

    scrStates = {f'V{i.lb}_{i.ub}' : i for i in scrIntervals} #'V00_10': Interval(0, 10)

    model = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03.xdsl"
    net = pysmile.Network()
    net.read_file(model)
    genderNH = net.get_node('Gender')
    genderPos = net.get_node_position(genderNH)
    # ======================
    scr_levelNH = net.get_node('Scr_level')
    scr_keys = list(scrStates.keys())
    initial_outcome_count = net.get_outcome_count(scr_levelNH)
    for i in range(0,len(scr_keys)):
        net.set_outcome_id(scr_levelNH,i,scr_keys[i])
    # ======================
    net.write_file("../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_prog_modified.xdsl")
    # ======================

    bnManipulation.print_cpt_matrix(net,genderNH)

    scrValsNH = net.get_node('Scr_level')
    net.set_outcome_id()





    print('End')

if __name__ == '__main__':
    main()
