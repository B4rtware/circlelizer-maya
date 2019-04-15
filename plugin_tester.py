"""
this file is used to quickly reload the plugin from within maya via browse plugin method
"""

import maya.cmds as cmds

cmds.unloadPlugin("Circlelizer.py",force = True)
cmds.loadPlugin("Circlelizer.py")
cmds.circlelize()
