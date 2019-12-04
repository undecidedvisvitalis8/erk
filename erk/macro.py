
import os
import sys
import glob
import json

INSTALL_DIRECTORY = sys.path[0]
SETTINGS_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "settings")
MACRO_DIRECTORY = os.path.join(SETTINGS_DIRECTORY, "macros")

# Load in macros
MACROS = []
target = os.path.join(MACRO_DIRECTORY, "*.json")
for file in glob.glob(target):
	with open(file, "r") as macrofile:
		data = json.load(macrofile)
		data["filename"] = file
		MACROS.append(data)

MACRO_LIST = {}
for m in MACROS:
	MACRO_LIST[ m["trigger"] ] = m["trigger"]+" "

#reload_macros()

def add_new_macro(macro):
	global MACROS
	global MACRO_LIST

	MACROS.append(macro)
	MACRO_LIST[ macro["trigger"] ] = macro["trigger"]+" "
