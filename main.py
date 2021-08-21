import utils

import pickle
import numpy as np

import sys
import pdb

try:
    historic_data = pickle.load(open("historic_data.pickle", "rb"))
except (OSError, IOError) as e:
    historic_data = utils.SeasonScraper()
    pickle.dump(historic_data, open("historic_data.pickle", "wb"))

utils.GenerateELO(historic_data)