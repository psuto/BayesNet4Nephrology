echo
call C:\Users\sutov\anaconda3\Scripts\activate.bat C:\Users\sutov\anaconda3\envs\dECMT

cd "../src"
python DataPreProcessing4GPv00.py --fds "C:\work\dev\dECMT_src\data_all\BN_nephro-onco_MIMIC_data\ph1_mimicAKI_v00_s00_test.csv" -n 100 --ppId "Ph2_GP_V00"

REM "Ph2_GP_V00"

cd "../batch files"

pause

