# B4rtware
# 2016 - 2020
# Circlelizer

import maya.api.OpenMaya as om
import math as m
import sys

# own classes and scripts
from QMessageDialog import QMessageDialog as QMessageDialog
from QMessageDialog import MESSAGE_ERROR, MESSAGE_INFORMATION
from QSlideInput import QSlideInput as QSlideInput
from apiHelper import createComponent, usingIterator_c, createComponent, convertMIterToList
from geogebraHelper import _createGeogebraPointString

import os

#+-----------------------------------------------------------------------------+
#| constants pre defined for easier usage                                      |
#+-----------------------------------------------------------------------------+

# modes for debugging purposes
# if the mode is set to debug every action outputs a message
# its basically a simple debug mechanic
DEBUG = 0
PUBLISH = 1

MODE = DEBUG

# version constant which will be used in the window title
VERSION = "v0.99"

#+-----------------------------------------------------------------------------+
#| Version Selection use 2017 or 2016 and below                                |
#+-----------------------------------------------------------------------------+
isVersion2017 = True
# try load load pyside2 which is used in 2017 and above
try:
    import PySide2.QtCore as qc 
    import PySide2.QtGui as qg
    import PySide2.QtWidgets as qw
except ImportError:
    import PySide.QtCore as qc
    import PySide.QtGui as qg
    # importing twice because under pyside2 a new submodule
    # was named QWidgets
    import PySide.QtGui as qw
    isVersion2017 = False

# used for independent argument assignments
from functools import partial

# for own command import (gui)
import maya.cmds as cmds

# determine which maya version is beeing used
is_version_2020 = cmds.about(version=True) == "2020"

## resolve the resource file paths
themes_path = os.environ["CIRCLELIZER_THEMES_PATH"]
docs_path = os.environ["CIRCLELIZER_DOCS_PATH"]
resources_path_unresolved = os.environ["XBMLANGPATH"]

fileObject = om.MFileObject()
fileObject.resolveMethod = om.MFileObject.kExact
fileObject.setRawPath(resources_path_unresolved)
fileObject.setRawName("header.png")
resources_path = fileObject.resolvedPath()

# load all the style files which are needed
styleSheet = None
with open(themes_path + "/default-theme.qss","r") as styleFile:
    styleSheet = styleFile.read()

aboutHTML = None
with open(docs_path + "/about.html", "r") as aboutFile:
    aboutHTML = aboutFile.read()

helpHTML = None
with open(docs_path + "/help.html", "r") as helpFile:
    helpHTML = helpFile.read()

#+-----------------------------------------------------------------------------+
#|                           QMessageDialog String                             |
#+-----------------------------------------------------------------------------+

MESSAGE_ERROR_ZERO_RADIUS = "The radius can not be zero!"
MESSAGE_ERROR_NEGATIVE_RADIUS = "The radius can not be negative!"
MESSAGE_ERROR_MORETHANONECOMPOENT = "You have selected more than one component!"

MESSAGE_INFORMATION_NOCOMPONENT ="You need to select a component!"

#+-----------------------------------------------------------------------------+
#|                            Plug-in Circlelizer                              |
#+-----------------------------------------------------------------------------+

class Circlelizer(om.MPxCommand):
    # Command Name
    kPluginCmdName = "circlelize"

    # Command Flags
    kHelpFlag = "-h"
    kHelpLongFlag = "-help"
    kRadiusFlag = "-r"
    kRadiusLongFlag = "-radius"
    kDegreeFlag = "-d"
    kDegreeLongFlag = "-degree"
    kMidPointFlag = "-m"
    kMidPointLongFlag = "-midPoint"
    kCircleNormalFlag = "-cn"
    kCircleNormalLongFlag = "-circleNormal"
    kProjectOnMeshFlag = "-p"
    kProjectOnMeshLongFlag = "-projectOnMesh"
    
    # Help Text
    kHelpText = "This command calculates a circle for the current selection."

    def __init__(self):
        om.MPxCommand.__init__(self)

        self.initDefaultValues()

        # for the redo function the calculated points must be stored, to
        # ensure that we dont need to calculate them again
        self.calculatedPoints = None
        self.orderedVerts = None

        # for the undo function we need to save our mdagpath to create
        # a mvertiter object and we need to save to previous postions of the
        # vertices
        self.mDagPath = None
        self.previousPositions = None

    def initDefaultValues(self):
        """initializes all of the variables so I can init again after a command
        use to reset the stats"""

        self.radius = None
        self.midPoint = None
        self.circleNormal = None
        self.projectOnMesh = False
        self.degree = 360

    @staticmethod
    def cmdCreator():
        return Circlelizer()

    @staticmethod
    def syntaxCreator():
        syntax = om.MSyntax()
        # Help Flag
        syntax.addFlag(Circlelizer.kHelpFlag,
                       Circlelizer.kHelpLongFlag)
        # Radius Flag
        syntax.addFlag(Circlelizer.kRadiusFlag,
                       Circlelizer.kRadiusLongFlag, om.MSyntax.kDouble)
        # Degree Flag
        syntax.addFlag(Circlelizer.kDegreeFlag,
                       Circlelizer.kDegreeLongFlag, om.MSyntax.kDouble)
        # MidPoint Flag
        syntax.addFlag(Circlelizer.kMidPointFlag,
                       Circlelizer.kMidPointLongFlag,(om.MSyntax.kDouble,
                                                      om.MSyntax.kDouble,
                                                      om.MSyntax.kDouble))
        # CircleNormal Flag
        syntax.addFlag(Circlelizer.kCircleNormalFlag,
                       Circlelizer.kCircleNormalLongFlag,(om.MSyntax.kDouble,
                                                          om.MSyntax.kDouble,
                                                          om.MSyntax.kDouble))
        # Project on Mesh Flag
        syntax.addFlag(Circlelizer.kProjectOnMeshFlag,
                       Circlelizer.kProjectOnMeshLongFlag, om.MSyntax.kBoolean)
        return syntax

    def argumentParser(self, args):
        argData = om.MArgParser(self.syntax(), args)
        # Radius Flag
        if argData.isFlagSet(Circlelizer.kRadiusFlag):
            self.radius = argData.flagArgumentDouble(Circlelizer.kRadiusFlag, 0)
        # Degree Flag
        if argData.isFlagSet(Circlelizer.kDegreeFlag):
            self.degree = argData.flagArgumentDouble(Circlelizer.kDegreeFlag, 0)
        # MidPoint Flag
        if argData.isFlagSet(Circlelizer.kMidPointFlag):
            self.midPoint = om.MPoint(
                argData.flagArgumentDouble(Circlelizer.kMidPointFlag, 0),
                argData.flagArgumentDouble(Circlelizer.kMidPointFlag, 1),
                argData.flagArgumentDouble(Circlelizer.kMidPointFlag, 2))
        # CircleNormal Flag
        if argData.isFlagSet(Circlelizer.kCircleNormalFlag):
            self.circleNormal = om.MVector(
                argData.flagArgumentDouble(Circlelizer.kCircleNormalFlag, 0),
                argData.flagArgumentDouble(Circlelizer.kCircleNormalFlag, 1),
                argData.flagArgumentDouble(Circlelizer.kCircleNormalFlag, 2))
        # Project on Mesh Flag
        if argData.isFlagSet(Circlelizer.kProjectOnMeshFlag):
            self.projectOnMesh = argData.flagArgumentBool(
                Circlelizer.kProjectOnMeshFlag, 0)

    def doIt(self, args):
        # before we are doing anything we need to pass the given arguments
        self.argumentParser(args)

        # get selected vertices and save the actual dagPath for later reference
        # inside the undo and redo function
        result = self._getSelectedVertices()
        # if an error occurs within getslectedvertices the function returns 0
        # otherwise it returns a tripel
        if result == None:
            self.initDefaultValues()
            return

        mDagPath, selectedVerts, selectedEdges = result

        self.mDagPath = mDagPath

        # create an iteration object for later iterations over the mesh surface
        vertComponent = createComponent(om.MFn.kMeshVertComponent,
                                        selectedVerts)
        mVertIter = om.MItMeshVertex(mDagPath, vertComponent.object())
        # before we can continue we need to order the vertices into a continues
        # selection
        orderedVerts = self._getContinuesSelection(mVertIter,
                                                   mDagPath,
                                                   selectedVerts,
                                                   selectedEdges)
        # we can now set the selection and convert it to a vertex selection
        meshName = mDagPath.fullPathName()
        selectionList = om.MSelectionList()
        for vert in orderedVerts:
            selectionList.add("{0}.vtx[{1}]".format(meshName, vert))
        om.MGlobal.setActiveSelectionList(selectionList)
        cmds.ConvertSelectionToContainedEdges()

        # now calculate all of the parameters we need. If non of the
        # paramters were passed, it will calculate average values but some
        # parameters dependend on some others
        # ----!!!! Because in this Version of the maya api we cant check 
        # whether a om.MPoint is None or not, we have to use a method called 
        # isinstance !!!! ----
        # because we need the average midPoint to move the selection into the
        # origin, we need to calculaute everytime the avg midPoint
        avgMidPoint = self._avgMidPoint(mVertIter)

        if not isinstance(self.midPoint, om.MPoint):
            self.midPoint = avgMidPoint
        if not isinstance(self.radius, float):
            self.radius = self._avgRadius(mVertIter, avgMidPoint)
        if not isinstance(self.circleNormal, om.MVector):
            self.circleNormal = self._avgNormal(mVertIter)
        # after the paramter asignments determine whether
        # the ordered selection is clockwise or anticlockwise
        isClockwise = self._isClockwiseOrder(mVertIter,
                                             orderedVerts,
                                             self.circleNormal)

        # if it is clockwise, reverse the ordered List because then the pre
        # calculated circle points maps to the correct position
        if isClockwise:
            orderedVerts = list(reversed(orderedVerts))

        # get the inner vertices for decide whether a vertex is a true border vertex or not used within the calculateTransforms function
        # it will also be used for the circlelation of the inner vertices
        firstInnerVerticesLoop, firstOuterVerticesLoop = self._getInnerOuterVertices(mVertIter,
                                                                                     orderedVerts,
                                                                                     avgMidPoint)

        # pre calculate the circle vertices postions
        circleVerts = self._calculateCircle(orderedVerts,
                                            self.degree,
                                            self.radius)

        transformedVerts = self._calculateTransforms(mVertIter,
                                                     circleVerts,
                                                     orderedVerts,
                                                     avgMidPoint,
                                                     self.radius,
                                                     self.circleNormal,
                                                     firstInnerVerticesLoop)

        # if the projectonmesh option was checked, recalculate the verticies
        # so they are matching the surface of the object
        if self.projectOnMesh:
            projectedVerts = self._projectVertsOnMeshSurface(mDagPath,
                                                             transformedVerts,
                                                             self.circleNormal,
                                                             self.midPoint)
            transformedVerts = projectedVerts

        # save some variables before tranform our vertices, for the undo redo
        # functions

        # save the current positions of the selected vertices
        self.previousPositions = self._getPositions(mVertIter, orderedVerts)
        # save for undo/redo
        self.orderedVerts = orderedVerts


        # now just apply the calculated positions to the actuall selected
        # vertices
        self._transformVerts(mVertIter, transformedVerts, orderedVerts,
                             self.midPoint)

        self.initDefaultValues()

    def undoIt(self):
        # we can only undo if we have every value we need
        if isinstance(self.previousPositions, list) and \
           isinstance(self.orderedVerts, list) and \
           isinstance(self.mDagPath, om.MDagPath):

            # create a mvertIter object to iterate over all the verts
            # and apply the previous position
            vertComponent = createComponent(om.MFn.kMeshVertComponent,
                                            self.orderedVerts)
            mVertIter = om.MItMeshVertex(self.mDagPath,
                                         vertComponent.object())

            for vert, position in zip(self.orderedVerts,
                                      self.previousPositions):
                mVertIter.setIndex(vert)
                mVertIter.setPosition(position)

            return True

        else:
            print(("[undoIt] saved parameter missing:"
                  "\nPreviousPositions: {0}"
                  "\nOrderedVerts: {1}"
                  "\nmDagPath: {2}").format(self.previousPositions,
                                            self.orderedVerts,
                                            self.mDagPath))

    def redoIt(self):
        # we can only redo if we have every value we need
        if isinstance(self.calculatedPoints, list) and \
           isinstance(self.orderedVerts, list) and \
           isinstance(self.mDagPath, om.MDagPath):

            # create a mVertIter object to iterate over all the verts and apply
            # again the calculated postitions
            vertComponent = createComponent(om.MFn.kMeshVertComponent,
                                            self.orderedVerts)
            mVertIter = om.MItMeshVertex(self.mDagPath, vertComponent.object())

            for vert, position in zip(self.orderedVerts, self.calculatedPoints):
                mVertIter.setIndex(vert)
                mVertIter.setPosition(position)
            return True

        else:
            print(("[redoIt] saved parameter missing:"
                  "\CalculatedPoints: {0}"
                  "\nOrderedVerts: {1}"
                  "\nmDagPath: {2}").format(self.calculatedPoints,
                                            self.orderedVerts,
                                            self.mDagPath))

    def isUndoable(self):
        return True

    @usingIterator_c
    def _calculateTransforms(self, mVertIter, circleVerts, orderedVerts,
                             midPoint, radius, circleNormal,
                             firstInnerVerticesLoop):
        """calculates new points for a circle

        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            circleVerts (List[om.MVector]): list of vertices which defines a circle
                and y is 0
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            midPoint (om.MPoint): middle point of the selection
            radius (float): radius for the circle
            circleNormal (om.MVector): direction the circle face is facing to
            

        Returns:\n
            List[om.MPoint]: a list of transform points which form a circle
        """

        orderedVertsPos = []
        #+---------------------------------------------------------------------+
        #| retrieve all positions of the ordered vertices (orderedVerts)       |
        #| and create a new list with all vertices moved to the origin         |
        #+---------------------------------------------------------------------+
        for vert in orderedVerts:
            mVertIter.setIndex(vert)
            orderedVertsPos.append(om.MPoint(mVertIter.position() - midPoint))

        #+---------------------------------------------------------------------+
        #| 1. get all surroundedVerts                                          |
        #| 2. move them to the origin                                          |
        #| 3. rotate them                                                      |
        #+---------------------------------------------------------------------+

        # first we will get the rotation for all of the verts
        rotationToPlane = circleNormal.rotateTo(om.MVector.kYaxisVector)

        # create a list of verts which will hold all surrounded vertices.
        # Including outer and inner Vertices
        surroundedVerts = []
        for vert in orderedVerts:
            mVertIter.setIndex(vert)
            # If a vertex has to or more connected neighbors which aren't
            # in the selection list it will calculates an average point.
            surroundedNeighbours = []
            #print("[DEBUG] vert = ({0})".format(vert))
            #print("[DEBUG] neighbours = ")
            for neighbour in mVertIter.getConnectedVertices():
                # if a neighbour isn't inside the list and not in the inner list
                # its an outer vertex
                #print("[DEBUG] n: {0} f: {1}".format(neighbour, firstInnerVerticesLoop))
                if neighbour not in orderedVerts and neighbour not in firstInnerVerticesLoop:
                    #print(neighbour)
                    mVertIter.setIndex(neighbour)
                    position = mVertIter.position()
                    # move to origin
                    position = position - midPoint
                    # append to list and rotate
                    surroundedNeighbours.append(
                        position.rotateBy(rotationToPlane))
            #print("\n")

            # if we find more then one surrounded neighbour at one vertex
            # we have to calculate the average of them
            newVert = om.MVector()
            surroundedNeighboursLen = len(surroundedNeighbours)

            #print("[DEBUG] vertex = ({0}) neighbours = {1}".format(orderedVertsPos, surroundedNeighbours))
            if surroundedNeighboursLen > 1:
                for vert in surroundedNeighbours:
                    newVert += vert
                newVert /= surroundedNeighboursLen
            elif surroundedNeighbours != []:
                newVert = surroundedNeighbours[0]
            else:
                # if there isnt any surrounded vert it is an true border vert
                # so we just use it as the surrounded vert
                newVert = om.MVector(mVertIter.position())

            # normalize the vector to apply our radius (inplace)
            newVert.normalize()
            newVert *= radius
            surroundedVerts.append(om.MPoint(newVert))

        #+---------------------------------------------------------------------+
        #| calculate average of rotation angle                                 |
        #+---------------------------------------------------------------------+
        avgAngle = 0
        #print(_createGeogebraPointString("surroundedVerts", surroundedVerts))
        #print(_createGeogebraPointString("circleVerts", circleVerts))
        for surroundedVert,circleVert  in zip(surroundedVerts, circleVerts):
            #print("[DEBUG] surrounded = ({0:>8.3f}, {1:>8.3f}, {2:>8.3f}) circleVert = ({3:>8.3f}, {4:>8.3f}, {5:>8.3f})".format(
            #    surroundedVert.x, surroundedVert.y, surroundedVert.z, circleVert.x, circleVert.y, circleVert.z))
            angle = m.atan2(surroundedVert.z,
                            surroundedVert.x) - m.atan2(circleVert.z,
                                                        circleVert.x)
            # It can happen that an really small value accours which should be
            # zero
            if angle < 0.0001 and angle > -0.0001:
                angle = 0.0

            if angle < 0:
                angle += 2*m.pi

            avgAngle += angle

        avgAngle /= len(circleVerts)

        #print("[DEBUG] avgAngle = {0}".format(avgAngle))

        # apply the rotation (YAW)
        rotation = om.MQuaternion(-avgAngle, om.MVector.kYaxisVector)
        #print("[DEBUG] rotation = {0}".format(rotation))

        rotatedCircleVerts = []
        for circleVert in circleVerts:
            rotatedVert = om.MVector(circleVert).rotateBy(rotation)
            # and now it can savely rerotated
            rotatedVert = rotatedVert.rotateBy(rotationToPlane.conjugate())
            rotatedCircleVerts.append(om.MPoint(rotatedVert))

        return rotatedCircleVerts

    @usingIterator_c
    def _getPositions(self, mVertIter, orderedVerts):
        """retrieves all positions from the mVertIter
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection

        Returns:\n
            List[om.MPoint]: list of position from the ordered vertices
        """
        positions = []
        for vert in orderedVerts:
            mVertIter.setIndex(vert)
            positions.append(mVertIter.position())

        return positions

    @usingIterator_c
    def _edgesToVerts(self, mItMeshEdgeComponent):
        """converts an edge selection into an vertices selection

        Args:\n
            mItMeshEdgeComponent (om.MItMeshEdge): iterator of edge
                components to be converted into vertices

        Returns:\n
            Set[int]: list of vertex id's        
        """

        # we create a set because then we dont need to care about if a vertex
        # was added twice
        edgeVertices = set()
        # iterate over every edge and add the new verts into the vertex list
        while not mItMeshEdgeComponent.isDone():
            edgeVertices.add(mItMeshEdgeComponent.vertexId(0))
            edgeVertices.add(mItMeshEdgeComponent.vertexId(1))
            mItMeshEdgeComponent.next()

        return edgeVertices

    @usingIterator_c
    def _facesToVerts(self, mItMeshPolygonComponent):
        """converts a face selection into a vertex selection

        Args:\n
            mItMeshPolygonComponent (om.MItMeshPolygon): iterator of polygon
                components to be converted into vertices

        Returns:\n
            Set[int]: list of vertex id's
        """

        # we create a set because then we dont need to care about if a vertex
        # was added twice
        faceVertices = set()
        # iterate over every face and add the new verts into the vertex list
        while not mItMeshPolygonComponent.isDone():
            verts = mItMeshPolygonComponent.getVertices()
            faceVertices.update(verts)
            if is_version_2020:
                mItMeshPolygonComponent.next()
            else:
                mItMeshPolygonComponent.next(None)

        return faceVertices

    @usingIterator_c
    def _transformVerts(self, mVertIter, calcedVerts, orderedVerts, midPoint):
        """applies the calculated new points onto the real points
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            calcedVerts (List[om.MPoint]): a list of transform points which form a circle
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            midPoint (om.MPoint): middle point of the selection

        Returns:\n
            None
        """
        # tempory: set midPoint to zero if projectOnMesh is activated
        # because it was already applied
        if self.projectOnMesh:
            midPoint = om.MPoint()

        # save the calculated points for redo function
        self.calculatedPoints = []
        for orderedVert, calcedVert in zip(orderedVerts, calcedVerts):
            mVertIter.setIndex(orderedVert)
            # because we rotated always at the origin we need to move
            # the vertex to the correct position via midPoint
            calcedVert += om.MVector(midPoint)
            self.calculatedPoints.append(calcedVert)
            mVertIter.setPosition(calcedVert)

    # TODO: check whether really the whole mVertIter object should be traversed and not \
    # only the orderedVerts same for radius
    @usingIterator_c
    def _avgMidPoint(self, mVertIter):
        """calculates the average point of all selected vertices
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected

        Returns:\n
            om.MPoint: middle point from the points of the mVertIter object
        """

        numVertices = mVertIter.count()
        avgMidPoint = om.MPoint()

        while not mVertIter.isDone():
            position = mVertIter.position()
            avgMidPoint += position
            mVertIter.next()

        return avgMidPoint/float(numVertices)

    @usingIterator_c
    def _avgRadius(self, mVertIter, avgMidPoint):
        """calculates the average radius of all selected vertices
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected

        Returns:\n
            float: average radius of the selection
        """

        radius = 0.0
        while not mVertIter.isDone():
            radius += mVertIter.position().distanceTo(avgMidPoint)
            mVertIter.next()

        return radius/float(mVertIter.count())

    @usingIterator_c
    def _avgNormal(self, mVertIter):
        """calculates the average normal of all points from the mVertIter
    
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected

        Returns:\n
            om.MVector: average normal (vector) from the mVertIter object
        """

        avgNormal = om.MVector()
        while not mVertIter.isDone():
            avgNormal += mVertIter.getNormal()
            mVertIter.next()

        return avgNormal/mVertIter.count()

    @usingIterator_c
    def _getContinuesSelection(self, mVertIter, mDagPath, selectedVerts,
                               selectedEdges):
        """reorders the given vertices into a continues selection.
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            mDagPath (om.MDagPath): path to the DAG node from the selection
            selectedVerts (List[int]): vertices id's of the selected vertices
            selectedEdges (List[int]): edge id's of the selected edges

        Returns:\n
            List[int]: list of vertices id's which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another one the selection
            
        """

        # create a temporary MItMeshEdge component to iterate over the edges
        mEdgeIter = om.MItMeshEdge(mDagPath)

        orderedVerts = []

        startEdge = selectedEdges.pop()
        mEdgeIter.setIndex(startEdge)
        # get a 'random' starting vertex
        startVert = mEdgeIter.vertexId(1)
        mVertIter.setIndex(startVert)
        orderedVerts.append(startVert)
        nextVert = startVert
        nextEdge = startEdge
        foundNoNextEdge = 0
        while True:
            # filter out the next edge which is inside the selection loop
            nextEdge = [edge
                        for edge in mVertIter.getConnectedEdges()
                        if edge in selectedEdges]
            if nextEdge == []:
                foundNoNextEdge += 1
            # if there isnt any nextEdges any more exit the loop
            if nextEdge == [] and selectedEdges != [] and foundNoNextEdge < 2:
                mEdgeIter.setIndex(startEdge)
                nextVert = mEdgeIter.vertexId(0)
                if nextVert not in orderedVerts:
                    orderedVerts.append(nextVert)
                mVertIter.setIndex(nextVert)
                continue
            elif nextEdge == []:
                break
            # remove it as its already used
            selectedEdges.remove(nextEdge[0])
            mEdgeIter.setIndex(nextEdge[0])
            # get the two connected vertecies of the edge
            # and filter out the vertex which was not previous selected
            connectedVerts = [mEdgeIter.vertexId(0), mEdgeIter.vertexId(1)]
            if nextVert == connectedVerts[0]:
                nextVert = connectedVerts[1]
            else:
                nextVert = connectedVerts[0]
            # choose if the vertex will be appanded at the beginning or at the
            # end
            if nextVert not in orderedVerts:
                orderedVerts.append(nextVert)

            mVertIter.setIndex(nextVert)

        return orderedVerts

    def _extractBorderVerts(self, mDagPath, selectedVerts):
        """extracts all border vertices from a given list of vertices
        
        Args:\n
            mDagPath (om.MDagPath): path to the DAG node from the selection
            selectedVerts (List[int]): vertices id's of the selected vertices

        Returns:\n
            Set[int]: collection of vertex id's which are forming the border
                of the selection (have neighbours which aren't inside the selection)
        """

        # create a new MItMeshVertex object to get the neighbours of the
        # vertex and only add those vertices which arent inside the
        # selectedVerts list
        vertComponent = createComponent(om.MFn.kMeshVertComponent,
                                        selectedVerts)
        mVertIter = om.MItMeshVertex(mDagPath, vertComponent.object())
        borderVertices = set()
        # vertices which are probably also a border vertex
        borderVerticesCandidates = set()

        while not mVertIter.isDone():
            # If a vertex is a true (end of surface) border vertex it can
            # be already added
            if mVertIter.onBoundary():
                borderVertices.add(mVertIter.index())
            else:
                for neighbour in mVertIter.getConnectedVertices():
                    if not neighbour in selectedVerts:
                        borderVertices.add(mVertIter.index())
                    else:
                        # if a vertex is surrounded by vertices which are all
                        # inside the selection it is possible that its a 
                        # corner vertex
                        #               +-+
                        #               +-o-+
                        #               +-+-+
                        # the o would be a corner vertex which does not have
                        # outer neighbours but is a border
                        #
                        # so we need to check whether a vertex which is not
                        # supposed to be a border vertex has at least two
                        # neighbours which are inside the border list
                        borderVerticesCandidates.add(neighbour)
            mVertIter.next()

        # now investigate the candidates if they are border vertices too
        for borderCandidate in borderVerticesCandidates:
            mVertIter.setIndex(borderCandidate)
            borderNeighbours = [neighbour
                                for neighbour in mVertIter.getConnectedVertices()
                                if neighbour in borderVertices]
            if len(borderNeighbours) > 1:
                # a vertex which has more than 2 border neighbours
                # it might be that this is also a border vertex
                # to check that we iterate over the vertices neighbours and
                # if they have both one neighbour match its a border vertex
                borderNeighbourSet = set()
                for borderNeighbour in borderNeighbours:
                    mVertIter.setIndex(borderNeighbour)
                    for neighbour in mVertIter.getConnectedVertices():
                        if neighbour not in selectedVerts:
                            if neighbour not in borderNeighbourSet:
                                borderNeighbourSet.add(neighbour)
                            else:
                                borderVertices.add(borderCandidate)
                                #print("[DEBUG] added " + borderCandidate)
        return borderVertices

    def _isClockwiseOrder(self, mVertIter, orderedVerts, avgNormal):
        """determines whether the given ordered list of verts is in a clockwise
        order or in an anti clockwise order
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            avgNormal (om.MVector): normal of the circle face facing direction

        Returns:\n
            bool: true if the circle is in clockwise order, false if not
        """

        orderedVertsLen = len(orderedVerts)
        # sum the determinants of all edges variable
        detSum = 0

        # because the equation only works for 2D we need to rotate the points
        # to a plane. I choosed the Y axis for that
        rotator = avgNormal.rotateTo(om.MVector.kYaxisVector)

        # go through all verts and first apply the rotation and then
        # calculate the determintante of the next 3 Verts till its again
        # at the start vert
        for i in range(orderedVertsLen):
            mVertIter.setIndex(orderedVerts[i])
            a = mVertIter.position()
            mVertIter.setIndex(orderedVerts[(i+1) % orderedVertsLen])
            b = mVertIter.position()
            mVertIter.setIndex(orderedVerts[(i+2) % orderedVertsLen])
            c = mVertIter.position()

            # before we can build the matrix we need to rotate the vertices
            aRot = om.MVector(a).rotateBy(rotator)
            bRot = om.MVector(b).rotateBy(rotator)
            cRot = om.MVector(c).rotateBy(rotator)

            matrix = om.MMatrix([[1, aRot.x, aRot.z, 0],
                                 [1, bRot.x, bRot.z, 0],
                                 [1, cRot.x, cRot.z, 0],
                                 [0,      0,      0, 0]])

            detSum += matrix.det3x3()

        if detSum < 0:
            return True
        else:
            return False

    def _getSelectedVertices(self):
        """returns the current selection as vertices and as loop. It only takes
        1 object into account
        
        Args:\n
            None

        Returns:\n
            (om.MDagPath, Set[int], Set[int]): path of the DAG node, collection of all selected
                vertices id's and edge id's
        """
        # get current component selection as a list
        mSelList = om.MGlobal.getActiveSelectionList()

        # throw an error message if no component was selected or to many
        if mSelList.isEmpty():
            error = QMessageDialog(MESSAGE_INFORMATION,
                                   MESSAGE_INFORMATION_NOCOMPONENT)
            error.exec_()
            return None

        # TODO: this is the function which will be adjusted to work for multiple
        # selections (getComponent(n))?
        # gets the first component in the list, the others are ignored
        mDagPath, mObj = mSelList.getComponent(0)

        # check which method for the specific type has to be used
        mObjType = mObj.apiType()
        selectedVerts = None
        selectedEdges = set()
        if mObjType == om.MFn.kMeshVertComponent:
            mVertIter = om.MItMeshVertex(mDagPath, mObj)
            selectedVerts = convertMIterToList(mVertIter)

        elif mObjType == om.MFn.kMeshEdgeComponent:
            mEdgeIter = om.MItMeshEdge(mDagPath, mObj)
            # convert edges to vertices
            selectedVerts = self._edgesToVerts(mEdgeIter)

        elif mObjType == om.MFn.kMeshPolygonComponent:
            mFaceIter = om.MItMeshPolygon(mDagPath, mObj)
            selectedVerts = self._facesToVerts(mFaceIter)

        # +--------------------------------------------------------------------+
        # | Determine if the current selection is a loop or not                |
        # +--------------------------------------------------------------------+
        extractBorder = False
        realBorderEdges = set()
        realBorderVerts = set()
        # create an temp iteration object
        vertComponent = createComponent(om.MFn.kMeshVertComponent,
                                        selectedVerts)
        mVertIter = om.MItMeshVertex(mDagPath, vertComponent.object())
        mEdgeIter = om.MItMeshEdge(mDagPath, vertComponent.object())

        # get all real border edges
        while not mEdgeIter.isDone():
            if mEdgeIter.onBoundary():
                vtx1 = mEdgeIter.vertexId(0)
                vtx2 = mEdgeIter.vertexId(1)
                if vtx1 in selectedVerts and vtx2 in selectedVerts:
                    realBorderEdges.add(mEdgeIter.index())
                    realBorderVerts.add(vtx1)
                    realBorderVerts.add(vtx2)
            mEdgeIter.next()

        # add the found border edges onto the empty set
        selectedEdges = realBorderEdges

        while not mVertIter.isDone():
            # get all neighbours of the selected verts which are also in the
            # selection list. If there are more than 2 verts its a loop
            selectedNeighbours = [neighbour
                                  for neighbour in mVertIter.getConnectedVertices()
                                  if neighbour in selectedVerts]

            if len(selectedNeighbours) > 2:
                extractBorder = True
                break

            mVertIter.next()

        if extractBorder:
            # use a shortcut function from cmds to extract the border edges
            cmds.ConvertSelectionToEdgePerimeter()
        else:
            # use a shortcut function from cmds to convert the vertices
            # selection into an edge selection
            cmds.ConvertSelectionToContainedEdges()

        # get the new selection
        mSelList = om.MGlobal.getActiveSelectionList()

        if not mSelList.isEmpty():
            # gets the first component in the list, the others are ignored
            mDagPath, mObj = mSelList.getComponent(0)

            mEdgeIter = om.MItMeshEdge(mDagPath, mObj)

            # get all edges for determine the ordered selection later
            while not mEdgeIter.isDone():
                selectedEdges.add(mEdgeIter.index())
                mEdgeIter.next()

            # convert the edge selection into verts selection
            selectedVerts = set.union(self._edgesToVerts(mEdgeIter), realBorderVerts)
        else:
            selectedVerts = realBorderVerts

        return mDagPath, selectedVerts, selectedEdges

    @usingIterator_c
    def _getInnerOuterVertices(self, mVertIter, orderedVerts, midpoint):
        """iterate over all ordered verts and for each vertex check which neighbours are closer than the ordered vertex
        
        Args:\n
            mVertIter (om.MItMeshVertex): iteration object which contains at least
                the vertices which are selected
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            midPoint (om.MVector): middle point of the selection

        Returns:\n
            (List[int], List[int]): list of inner vertices and outer vertices id's
        """
        # FIXME: so this only works if the mesh does not have overlapping geometry inside the selection (eventually  it can be checked with isPlanar
        # so check if the selection has planar faces) 
        innerVertices = []
        outerVertices = []
        for vertex in orderedVerts:
            mVertIter.setIndex(vertex)
            # get vertex position
            vertexPosition = mVertIter.position()
            # get vertex distance to midpoint
            vertexDistanceToMid = vertexPosition.distanceTo(midpoint)
            # iterate over each neighbour and check the distance to the midpoint
            for neighbour in mVertIter.getConnectedVertices():
                mVertIter.setIndex(neighbour)
                neighbourPosition = mVertIter.position()
                neighbourDistanceToMid = neighbourPosition.distanceTo(midpoint)
                if (neighbour not in innerVertices and neighbour not in orderedVerts and neighbourDistanceToMid <= vertexDistanceToMid):
                    innerVertices.append(neighbour)
                else:
                    outerVertices.append(neighbour)

        return (innerVertices, outerVertices)

    def _calculateCircle(self, orderedVerts, margin, radius):
        """calculates each section and creates a circle out of that
        
        Args:\n
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            margin (float): degree of the circle section default (360)
            radius (float): radius of the circle

        Returns:\n
            List[om.MPoint]: a list of transform points which form a circle
        """

        phi = 0.0
        alpha = float(margin)/float(len(orderedVerts))
        sectionDegree = 0

        calcedPoints = []

        #print("[DEBUG] calculate circle:")
        for n in range(len(orderedVerts)):
            # convert degree in radiant
            phi = sectionDegree * (m.pi/180.0)

            # calculate points
            x = radius * m.cos(phi)
            z = radius * m.sin(phi)
            #print("[DEBUG] ({0:>8.3f}, {1:>8.3f}, {2:>8.3f})".format(x, 0, z))
            calcedPoints.append(om.MVector(x, 0, z))

            sectionDegree += alpha

        return calcedPoints

    def _projectVertsOnMeshSurface(self, mDagPath, orderedVerts, avgNormal,
                                   midPoint):
        """project the vertices onto the surface so calculate the circle in place

        Args:\n
            mDagPath (om.MDagPath): path to the DAG node from the selection
            orderedVerts (List[int]): list of vertices ids which form a continues
                row (or circle) every neighbor in the list is a neighbor of one
                another on the selection
            avgNormal (om.MVector): normal of the circle
            midPoint (om.MPoint): middle point of the circle

        Returns:\n
            List[om.MPoint]: list of all projected points positions
        """
        meshToProjectOn = om.MFnMesh(mDagPath)
        projectedVerts = []
        for startPoint in orderedVerts:
            tranformedCirclePoint = om.MFloatPoint(startPoint +
                                                   om.MVector(midPoint))
            rayHit = meshToProjectOn.closestIntersection(tranformedCirclePoint,
                                                         om.MFloatVector(avgNormal),
                                                         om.MSpace.kObject, 100.0,
                                                         True)
            projectedVerts.append(om.MPoint(rayHit[0]))
        return projectedVerts

# +----------------------------------------------------------------------------+
# |             Graphical User Interface QTDialog (info/about) Qt Class        |
# +----------------------------------------------------------------------------+
class CirclelizerInfoInterfaceClass(qw.QDialog):
    TEXT_AREA_HEIGHT = 400
    TEXT_AREA_WIDTH = 400

    def __init__(self, stylelize):
        qw.QDialog.__init__(self)
        
        self.setWindowIcon(qg.QIcon(resources_path + "help.png"))
        self.setWindowTitle("Circlelizer Help")
        if stylelize: self.setStyleSheet(styleSheet)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.initMainWidget()

    def initMainWidget(self):
        self.mainLayout = qw.QVBoxLayout()
        self.tabWidget = qw.QTabWidget()
        self.tabWidget.addTab(self.initTabHelp(),
                            qg.QIcon(resources_path + "help.png"),
                            "Help")
        self.tabWidget.addTab(self.initTabAbout(),
                            qg.QIcon(resources_path + "about.png"),
                            "About")
        
        self.mainLayout.addWidget(self.tabWidget)

        self.setLayout(self.mainLayout)

    def initTabHelp(self):
        self.tabHelp = qw.QWidget()
        self.tabHelp.setObjectName("tab-help")

        layout = qw.QVBoxLayout()

        self.te_help = qw.QTextBrowser()
        self.te_help.setReadOnly(True)
        self.te_help.setHtml(helpHTML)
        self.te_help.setFixedSize(self.TEXT_AREA_HEIGHT, self.TEXT_AREA_WIDTH)
        layout.addWidget(self.te_help)

        self.tabHelp.setLayout(layout)

        return self.tabHelp

    def initTabAbout(self):
        self.tabAbout = qw.QWidget()
        self.tabAbout.setObjectName("tab-about")

        layout = qw.QHBoxLayout()

        self.te_about = qw.QTextBrowser()
        self.te_about.setReadOnly(True)
        self.te_about.setHtml(aboutHTML)
        self.te_about.setMaximumSize(self.TEXT_AREA_HEIGHT,
                                     self.TEXT_AREA_WIDTH)
        layout.addWidget(self.te_about)

        self.tabAbout.setLayout(layout)

        return self.tabAbout

#+-----------------------------------------------------------------------------+
#|                      Graphical User Interface QT Class                      |
#+-----------------------------------------------------------------------------+

class CirclelizerInterfaceClass(qw.QWidget):
    # Widgets Variables
    WIDGET_HEIGHT = 20
    SI_WIDTH = 50
    SI_NORMAL_XYZ_WIDTH = 25
    SI_MIDPOINT_XYZ_WIDTH = 50

    B_NORMAL_WIDTH = 25

    def __init__(self, slideInput, stylelize, logo):
        qw.QWidget.__init__(self)
        self.infoDialog = CirclelizerInfoInterfaceClass(stylelize)

        self.input = QSlideInput if slideInput else partial(qw.QLineEdit, "0.0")

        self.setWindowIcon(qg.QIcon(resources_path+"icon.png"))
        self.setWindowTitle("Circlelizer {0}".format(VERSION))
        self.setObjectName("body")
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        if stylelize: self.setStyleSheet(styleSheet)

        self.initMainWidget(logo)

    def initMainWidget(self, logo):
        layout = qw.QGridLayout()

        # Header Label
        if logo:
            self.l_header = qw.QLabel()
            self.l_header.setPixmap(qg.QPixmap(resources_path+"header_70.png"))
            self.l_header.setAlignment(qc.Qt.AlignCenter)
            layout.addWidget(self.l_header, 0, 0)

        # Help Button
        icoHelp = qg.QIcon(resources_path + "help.png")
        self.b_help = qw.QPushButton()
        self.b_help.setObjectName("b_help")
        self.b_help.setIcon(icoHelp)
        self.b_help.setFixedSize(self.WIDGET_HEIGHT, self.WIDGET_HEIGHT)
        self.b_help.setIconSize(qc.QSize(self.WIDGET_HEIGHT,self.WIDGET_HEIGHT))
        self.b_help.setLayoutDirection(qc.Qt.RightToLeft)
        self.b_help.clicked.connect(self.On_HelpButton_Pressed)
        layout.addWidget(self.b_help, 0, 0, qc.Qt.AlignTop)

        # Tab Widgets
        self.t_basic = qw.QTabWidget()
        self.initTabBasic()
        layout.addWidget(self.t_basic, 1, 0)

        self.t_advanced = qw.QTabWidget()
        self.initTabAdvanced()
        layout.addWidget(self.t_advanced, 2, 0)

        # Circlelize Button
        self.b_circlize = qw.QPushButton("Circlelize")
        self.b_circlize.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_circlize.clicked.connect(self.On_CirclizeButton_Pressed)
        layout.addWidget(self.b_circlize, 3, 0)

        self.setLayout(layout)

    def initTabBasic(self):
        self.tabBasic = qw.QWidget()
        self.tabBasic.setObjectName("tab-basic")
        self.t_basic.addTab(self.tabBasic,
                            qg.QIcon(resources_path + "tool.png"),
                            "Basic")
        # Widgets
        layout = qw.QGridLayout()
        # 0 0 Radius Checkbox
        self.cb_radius = qw.QCheckBox("Smart Radius")
        self.cb_radius.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_radius.setChecked(True)
        self.cb_radius.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value,[self.si_radius,
                                                      self.l_radius]))
        layout.addWidget(self.cb_radius, 0, 0)

        # 1 0 MidPoint CheckBox
        self.cb_midPoint = qw.QCheckBox("Smart MidPoint")
        self.cb_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_midPoint.setChecked(True)
        self.cb_midPoint.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_midPointX,
                                                       self.si_midPointY,
                                                       self.si_midPointZ,
                                                       self.l_midPoint]))
        layout.addWidget(self.cb_midPoint, 1, 0)

        # 0 1 Normal Checkbox
        self.cb_normal = qw.QCheckBox("Smart Normal")
        self.cb_normal.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_normal.setChecked(True)
        self.cb_normal.stateChanged.connect(
            lambda value:
            self.On_SmartCheckBox_StateChanged(value, [self.si_normalX,
                                                       self.si_normalY,
                                                       self.si_normalZ,
                                                       self.b_normalX,
                                                       self.b_normalY,
                                                       self.b_normalZ,
                                                       self.l_normal]))
        layout.addWidget(self.cb_normal, 0, 1)

        # 1 1 Project on Mesh
        self.cb_projectOnMesh = qw.QCheckBox("project on mesh")
        self.cb_projectOnMesh.setFixedHeight(self.WIDGET_HEIGHT)
        self.cb_projectOnMesh.setChecked(False)
        layout.addWidget(self.cb_projectOnMesh, 1, 1)

        self.tabBasic.setLayout(layout)

    def initTabAdvanced(self):
        self.tabAdvanced = qw.QWidget()
        self.tabAdvanced.setObjectName("tab-advanced")
        self.t_advanced.addTab(self.tabAdvanced,
                               qg.QIcon(resources_path + "advanced.png"),
                               "Advanced")

        # Widgets
        layout = qw.QGridLayout()

        # +--------+
        # | Radius |
        # +--------+

        # 0 1 Radius Label
        self.l_radius = qw.QLabel("Radius: ")
        self.l_radius.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_radius, 0, 0)

        # 0 2 Radius SlideInput
        self.si_radius = self.input()
        self.si_radius.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        layout.addWidget(self.si_radius, 0, 1)

        # +--------+
        # | Degree |
        # +--------+

        self.l_degree = qw.QLabel("Degree:")
        self.l_degree.setFixedHeight(self.WIDGET_HEIGHT)
        self.l_degree.setFixedWidth(45)
        layout.addWidget(self.l_degree, 0, 2)

        self.si_degree = self.input()
        self.si_degree.setText("360.0")
        self.si_degree.setFixedSize(self.SI_WIDTH, self.WIDGET_HEIGHT)
        self.si_degree.setToolTip("does not 100% works with my calculations you"\
                                  "\nhave to manual adjust "\
                                  "the rotation and scale.")
        layout.addWidget(self.si_degree, 0, 3)

        # +----------+
        # | MidPoint |
        # +----------+

        # 2 1 MidPoint Label
        self.l_midPoint = qw.QLabel("MidPoint: ")
        self.l_midPoint.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_midPoint, 1, 0)

        # 2 2 MidPoint SlideInput X
        self.si_midPointX = self.input()
        self.si_midPointX.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointX.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointX, 1, 1)

        # 2 3 MidPoint SlideInput Y
        self.si_midPointY = self.input()
        self.si_midPointY.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointY.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointY, 1, 2)

        # 2 4 MidPoint SlideInput Z
        self.si_midPointZ = self.input()
        self.si_midPointZ.setFixedWidth(self.SI_MIDPOINT_XYZ_WIDTH)
        self.si_midPointZ.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.si_midPointZ, 1, 3)

        # +--------+
        # | Normal |
        # +--------+

        # 2 0 Normal Label
        self.l_normal = qw.QLabel("Circle Normal:")
        self.l_normal.setFixedHeight(self.WIDGET_HEIGHT)
        layout.addWidget(self.l_normal, 2, 0)

        # 2 1 Child Normal X HBoxLayout
        # -----------------------------
        childNormalXLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput X
        self.si_normalX = self.input()
        self.si_normalX.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalXLayout.addWidget(self.si_normalX)

        # 0 1 Normal Button X 
        self.b_normalX = qw.QPushButton("X")
        self.b_normalX.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalX.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalX.setObjectName("xyz")
        self.b_normalX.pressed.connect(lambda:self.On_AxisButton_Pressed("X"))
        childNormalXLayout.addWidget(self.b_normalX)

        layout.addItem(childNormalXLayout, 2, 1)

        # 2 2 Child Normal Y HBoxLayout
        # -----------------------------
        childNormalYLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Y
        self.si_normalY = self.input()
        self.si_normalY.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalYLayout.addWidget(self.si_normalY)

        # 0 1 Normal Button Y
        self.b_normalY = qw.QPushButton("Y")
        self.b_normalY.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalY.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalY.setObjectName("xyz")
        self.b_normalY.pressed.connect(lambda:self.On_AxisButton_Pressed("Y"))
        childNormalYLayout.addWidget(self.b_normalY)

        layout.addItem(childNormalYLayout, 2, 2)

        # 2 3 Child Normal Z HBoxLayout
        # -----------------------------
        childNormalZLayout = qw.QHBoxLayout()

        # 0 0 Normal SlideInput Z
        self.si_normalZ = self.input()
        self.si_normalZ.setFixedWidth(self.SI_NORMAL_XYZ_WIDTH)
        self.si_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        childNormalZLayout.addWidget(self.si_normalZ)

        # 0 1 Normal Button Z
        self.b_normalZ = qw.QPushButton("Z")
        self.b_normalZ.setFixedWidth(self.B_NORMAL_WIDTH)
        self.b_normalZ.setFixedHeight(self.WIDGET_HEIGHT)
        self.b_normalZ.pressed.connect(lambda:self.On_AxisButton_Pressed("Z"))
        childNormalZLayout.addWidget(self.b_normalZ)

        layout.addItem(childNormalZLayout, 2, 3)

        # Call events
        self.cb_radius.stateChanged.emit(2)
        self.cb_midPoint.stateChanged.emit(2)
        self.cb_normal.stateChanged.emit(2)

        self.tabAdvanced.setLayout(layout)

    def On_SmartCheckBox_StateChanged(self, value, instances):
        if value == 2:
            for instance in instances:
                instance.setDisabled(1)
        elif value == 0:
            for instance in instances:
                instance.setDisabled(0)

    def On_HelpButton_Pressed(self):
        self.infoDialog.show()

    def On_AxisButton_Pressed(self, axis):
        if axis == "X":
            self.si_normalX.setText("1.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Y":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("1.0")
            self.si_normalZ.setText("0.0")
        elif axis == "Z":
            self.si_normalX.setText("0.0")
            self.si_normalY.setText("0.0")
            self.si_normalZ.setText("1.0")

    def On_CirclizeButton_Pressed(self):
        partialCirclelize = None

        if isVersion2017:
            partialCirclelize = partial(cmds.circlelize)
        else:
            # this version of python does not fully support partial.keywords
            # if its empty it returns None
            # so we use a little trick here: initialize the function 
            # with a dummy variable
            partialCirclelize = partial(cmds.circlelize, dummy = None)

        if not self.cb_radius.isChecked():
            radius = float(self.si_radius.text())

            if radius == 0:
                error = QMessageDialog(MESSAGE_ERROR,
                                       MESSAGE_ERROR_ZERO_RADIUS)
                error.exec_()
                return
            elif radius < 0:
                error = QMessageDialog(MESSAGE_ERROR,
                                       MESSAGE_ERROR_NEGATIVE_RADIUS)
                error.exec_()
                return
                            
            partialCirclelize.keywords["r"] = radius

        if not self.cb_midPoint.isChecked():
            midPoint = (float(self.si_midPointX.text()),
                        float(self.si_midPointY.text()),
                        float(self.si_midPointZ.text()))

            partialCirclelize.keywords["m"] = midPoint

        if not self.cb_normal.isChecked():
            normal = (float(self.si_normalX.text()),
                      float(self.si_normalY.text()),
                      float(self.si_normalZ.text()))
            partialCirclelize.keywords["cn"] = normal

        degree = float(self.si_degree.text())
        partialCirclelize.keywords["d"] = degree

        projectOnMesh = self.cb_projectOnMesh.isChecked()
        partialCirclelize.keywords["p"] = projectOnMesh

        if not isVersion2017:
            # remove our dummy arg
            partialCirclelize.keywords.pop("dummy")

        partialCirclelize()

#+-----------------------------------------------------------------------------+
#|                      Plug-in Graphical User Interface                       |
#+-----------------------------------------------------------------------------+

class CirclelizerInterface(om.MPxCommand):
    kPluginCmdName = "circlelizerInterface"

    kHelpFlag = "-h"
    kHelpLongFlag = "-help"
    kSlideInputFlag = "-si"
    kSlideInputLongFlag = "-slideInput"
    kStylelizeFlag = "-s"
    kStylelizeLongFlag = "-stylelize"
    kLogoFlag = "-l"
    kLogoLongFlag = "-logo"

    kHelpText = "creates an interface for the circlelize command"

    def __init__(self):
        om.MPxCommand.__init__(self)
        self.initDefaultValues()

    def initDefaultValues(self):
        self.stylize = True
        if isVersion2017:
            self.slideInput = True
        else:
            self.slideInput = False
        self.logo = True

    @staticmethod
    def cmdCreator():
        return CirclelizerInterface()

    @staticmethod
    def syntaxCreator():
        syntax = om.MSyntax()
        # Help Flag
        syntax.addFlag(CirclelizerInterface.kHelpFlag,
                       CirclelizerInterface.kHelpLongFlag)

        # Enable SlideInput Flag
        syntax.addFlag(CirclelizerInterface.kSlideInputFlag,
                       CirclelizerInterface.kSlideInputLongFlag,
                       om.MSyntax.kBoolean)

        # DisableStyle Flag
        syntax.addFlag(CirclelizerInterface.kStylelizeFlag,
                       CirclelizerInterface.kStylelizeLongFlag,
                       om.MSyntax.kBoolean)

        # Logo Flag
        syntax.addFlag(CirclelizerInterface.kLogoFlag,
                       CirclelizerInterface.kLogoLongFlag,
                       om.MSyntax.kBoolean)

        return syntax

    def argumentParser(self, args):
        argData = om.MArgParser(self.syntax(), args)

        # Help Flag
        if argData.isFlagSet(CirclelizerInterface.kHelpFlag):
            self.setResult(CirclelizerInterface.kHelpText)
        # Enable SlideInput Flag
        if argData.isFlagSet(CirclelizerInterface.kSlideInputFlag):
            self.slideInput = argData.flagArgumentBool(
                CirclelizerInterface.kSlideInputFlag, 0)
        # DisableStyle Flag
        if argData.isFlagSet(CirclelizerInterface.kStylelizeFlag):
            self.stylize = argData.flagArgumentBool(
                CirclelizerInterface.kStylelizeFlag, 0)
        # Logo Flag
        if argData.isFlagSet(CirclelizerInterface.kLogoFlag):
            self.logo = argData.flagArgumentBool(
                CirclelizerInterface.kLogoFlag, 0)

    def doIt(self, args):
        self.argumentParser(args)

        self.cuiClass = CirclelizerInterfaceClass(self.slideInput,
                                                  self.stylize,
                                                  self.logo)
        self.cuiClass.show()

#+-----------------------------------------------------------------------------+
#|                           Plug-in initialization                            |
#+-----------------------------------------------------------------------------+
commands = [Circlelizer, CirclelizerInterface]

def maya_useNewAPI():
    pass

def initializePlugin(mObject):
    mPlugin = om.MFnPlugin(mObject, vendor = "B4rtware", version = VERSION[1:])

    for command in commands:
        try:
            mPlugin.registerCommand(command.kPluginCmdName,
                                    command.cmdCreator,
                                    command.syntaxCreator)
        except:
            sys.stderr.write("Failed to register command: {0}".format(
                command.kPluginCmdName))

def uninitializePlugin(mObject):
    mPlugin = om.MFnPlugin(mObject)

    for command in commands:
        try:
            mPlugin.deregisterCommand(command.kPluginCmdName)
        except:
            sys.stderr.write("Failed to unregister command: {0}".format(
                command.kPluginCmdName))
