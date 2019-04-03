import maya.api.OpenMaya as om

#+---------------------------------------------------------------------------+
#|                         Maya Api Helper Functions                         |
#|                                                                           |
#| -> A collection of usefull functions for the maya api                     |
#+---------------------------------------------------------------------------+
def getPath(path, resolveMethod):
    fileObject = om.MFileObject()
    fileObject.resolveMethod = resolveMethod
    fileObject.setRawPath(path)
    return fileObject.resolvedPath()

def convertMIterToList(mVertIter):
    """
    if everything would function as it should, this function wouldnt be
    necessary. It only accepts mItMeshVertex objects and returns a list of
    vertices"""

    vertices = []
    while not mVertIter.isDone():
        vertices.append(int(mVertIter.index()))
        mVertIter.next()

    return vertices

def usingIterator(function):
    """
    use this as an decorator if you are using a mMeshVertexIterator or
    something similarly. Before it calls the actual function its resets
    the iterator and if the function is completed it resets the iterator again.

    The iterator must be in the first place of the parameter list.
    
    ! only use this method if you DOESN'T want to call it inside a class !"""
    def wrapper(*args, **kwargs):
        args[0].reset()
        result = function(*args, **kwargs)
        args[0].reset()

        return result
    return wrapper

def usingIterator_c(function):
    """
    use this as an decorator if you are using a mMeshVertexIterator or
    something similarly. Before it calls the actual function its resets
    the iterator and if the function is completed it resets the iterator again.

    The iterator must be in the first place after self of the parameter list.
    
    ! only use this method if you want to call it inside a class !"""
    def wrapper(*args, **kwargs):
        args[1].reset()
        result = function(*args, **kwargs)
        args[1].reset()

        return result
    return wrapper

def createComponent(MfnMeshComponentType, data):
    """
    creates a new component with given data.

    ! only works for polygon objects !"""

    # create a new component
    component = om.MFnSingleIndexedComponent()
    # of type <MfnMeshComponentType>
    component.create(MfnMeshComponentType)
    # and adding the data
    component.addElements(data)

    return component