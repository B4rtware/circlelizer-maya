import maya.cmds as cmds

cmds.unloadPlugin("Circlelizer.py",force = True)
cmds.loadPlugin("Circlelizer.py")
cmds.circlelize()