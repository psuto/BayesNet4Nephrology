import param4BN_learn_from_data_tranfs as parBN
import pysmile
# pysmile_license is your license key
import pysmile_license

from bnManipulation import BNManipulation

# bnManipulation = BNManipulation()

def main():
    scrStates= parBN.scrStates
    ageStates = parBN.ageStates
    aki48H_states  = parBN.aki48H_states

    model = "../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03.xdsl"
    net = pysmile.Network()
    net.read_file(model)
    genderNH = net.get_node('Gender')
    genderPos = net.get_node_position(genderNH)
    # ======================
    nodeId='Scr_level'
    scr_levelNH = net.get_node(nodeId)
    scr_keys = list(scrStates.keys())
    BNManipulation.updateNodeOutcomes(net,nodeId,scr_keys)
    # initial_outcome_count = net.get_outcome_count(scr_levelNH)
    # for i in range(0,len(scr_keys)):
    #     net.set_outcome_id(scr_levelNH,i,scr_keys[i])
    # ======================
    nodeId = 'Age'
    age_levelNH = net.get_node(nodeId)
    age_keys = list(ageStates.keys())
    BNManipulation.updateNodeOutcomes(net, nodeId, age_keys)
    # ======================
    nodeId = 'AKI48H'
    age_levelNH = net.get_node(nodeId)
    BNManipulation.updateNodeOutcomes(net, nodeId, aki48H_states)
    # ======================
    # initial_outcome_count = net.get_outcome_count(age_levelNH)
    # for i in range(0,len(age_keys)):
    #     net.set_outcome_id(age_levelNH,i,age_keys[i])
    # ======================

    # ======================
    net.write_file("../models/AKI prediction_Stage_1_Learning_wo_Drug_v004_order03_4_training.xdsl")
    # ======================
    # bnManipulation.print_cpt_matrix(net,genderNH)
    print('End')

# List of node names to learn: 'Gender' , 'Age' , 'AKI48H' , 'Scr_level'

if __name__ == '__main__':
    main()
