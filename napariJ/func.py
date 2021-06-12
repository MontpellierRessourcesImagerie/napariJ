from jpype import *
# Enable Java imports
import jpype.imports
# Pull in types
from jpype.types import *
import os
from pathlib import Path
import numpy as np
from PyQt5 import QtCore, QtWidgets
import jupyter_client

def startFIJI(aPath):
    os.chdir(aPath)
    startJVM(
        aPath + "/java/linux-amd64/jdk1.8.0_172/jre/lib/amd64/server/libjvm.so",
        "-ea",
        "-Dpython.cachedir.skip=false",
        "-Djdk.gtk.version=3",
        "-Dplugins.dir=.",
        "-Xmx19639m",
        "-Djava.class.path=./jars/imagej-launcher-5.0.3.jar",
        "-Dimagej.dir=.",
        "-Dij.dir=.",
        "-Dfiji.dir=.",
        "-Dij.executable= "
    )
    for path in Path('./jars').rglob('*.jar'):
        addClassPath(aPath + str(path))
    for path in Path('./plugins').rglob('*.jar'):
        addClassPath(aPath + str(path))
    from net.imagej.launcher import ClassLauncher
    ClassLauncher.main(("-ijjarpath", "jars", "-ijjarpath", "plugins", "net.imagej.Main"))
    from ij import IJ, ImageJ
    IJ.setProperty('jupter_connection_file', jupyter_client.find_connection_file())

def displayActiveImageInNewWindow():
    from ij import IJ, ImageJ
    from ij.plugin import HyperStackConverter
    import napari
    image = IJ.getImage()
    cal = image.getCalibration()
    zFactor = cal.getZ(1) / cal.getX(1)
    title = image.getShortTitle()
    shift = 128
    bitDepth = image.getBitDepth()
    if bitDepth==16:
        shift = 32768
    dims = list(image.getDimensions())
    print(dims)
    isHyperStack = image.isHyperStack()
    HyperStackConverter.toStack(image)
    stackDims = list(image.getDimensions())
    dim = stackDims[3]
    if stackDims[2] == 1 and stackDims[3] == 1 and stackDims[4] > 1:
        dim = dims[4]
    pixels = np.array(image.getStack().getVoxels(0, 0, 0, stackDims[0], stackDims[1], dim, [])) + shift
    if isHyperStack:
        image2 = HyperStackConverter.toHyperStack(image, dims[2], dims[3], dims[4], "Composite");
        image.close()
        image2.show()
    viewer = napari.Viewer()
    viewer.theme = 'dark'
    colors = ['magenta', "cyan", "yellow", "red", "green", "blue"]
    for c in range(0, dims[2]):
        viewer.add_image(pixels.reshape(dims[4], dims[3], dims[2], dims[1], dims[0])[:, :, c, :, :],
                         name="C" + str(c + 1) + "-" + str(title),
                         colormap=colors[c],
                         blending='additive',
                         scale=[zFactor, 1, 1])
    viewer.dims.ndisplay = 3
    return viewer
