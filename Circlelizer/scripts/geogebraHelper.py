#+---------------------------------------------------------------------------+
#|                   Geogebra Debugging Helper Functions                     |
#|                                                                           |
#| -> I often use GeoGebra to check my math so I have some functions which   |
#|    helps with that                                                        |
#+---------------------------------------------------------------------------+

def _createGeogebraPointString(name, listOfPointPositions, rounding = 6):
    pointStringTemplate = "({0.x:.{1}f},{0.y:.{1}f},{0.z:.{1}f})"
    pointString = "{0} = ".format(name) + "{"
    for i in range(len(listOfPointPositions) - 1):
        pointString += pointStringTemplate.format(listOfPointPositions[i],
                                                  rounding)+","

    pointString += pointStringTemplate.format(listOfPointPositions[-1],
                                              rounding)+"}"

    return pointString