import os
os.environ["MEDLEYDB_PATH"] = os.path.expanduser("~/datasets/MedleyDB")

import DeepInstruments.audio
import DeepInstruments.learning
import DeepInstruments.main
import DeepInstruments.singlelabel
import DeepInstruments.symbolic
import DeepInstruments.wrangling