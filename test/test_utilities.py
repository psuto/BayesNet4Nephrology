import pytest as pt
import utilities as u

@pt.mark.parametrize("fileName",['test'])
def test_extract_info_from_model_file_name_general(fileName):
    info = u.extractInfoFromModelFileNameGeneral(fileName)
    assert False
