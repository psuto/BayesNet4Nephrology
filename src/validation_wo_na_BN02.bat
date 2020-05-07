REM inputModelFile --fm
REM inputDataSetFile --fds
python validation.py --fm "../models/BN02_AKI_prediction_Stage_1_Learning_wo_Drug_v004_4timeSteps_2nd_order_training.xdsl"  --fds "C:\Work\dev\dECMT_src\data\AKI_data_200325_full_dob_v02_forBN_wo_NA_ri_0_ri2_217148_ro_93120_20-04-24_23-30-27.csv" --nfold 5 --tnode "AKI48H" --outcidx 0