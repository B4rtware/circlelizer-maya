# circlelizer-maya

![cover image for circlelizer-maya](resources/cover.png)

**Circlelizer** is a plugin for Maya which is written in Python with *Maya API 2.0*. It generates a circle from a given selection. You can either let the program calculate all parameters or define your own.

---

**_Note_**: use this plugin at you own risk. Save your project each time before you are using it. In my test cases I hadn't any real problems but I can't test every little edge case. Keep in mind that this plugin is still in development.

![example](resources/example_01.png)

## GUI
![gui](resources/gui_view098.png)

its also possible to deactive the style:

![gui](resources/gui_view_nostyle098.png)

## Changelog
***Latest Versions:***

circlelize v0.98
circlelizerInterface v2.0


***v0.98 Changelog***

- merged version files
- updated mod file for merged Maya files (important: use the new mod file)
- added projection on mesh
- improved border edge extraction
- removed temporary extract border flag

## Installation Instructions

Clone the repo and place the folder `Circlelizer` to your prefered location. An icon for the shelf is inside the icons folder (icon.png).

Replace the **\<enter here full path\>** with the full path to your circlelizer folder in the **circlelizer.mod** file.

Now, copy **circlelizer.mod** into:

- <code>users/\<yourname>/documents/maya/modules</code> - for any maya version
- <code>programs/autodesk/maya\<version>/modules</code> - for the <version> specific maya version


Inside Maya you need to go to <code>Windows -> Settings/Preferences -> Plug-in Manager</code> search for the circlelizer tab and load it manually and/or tick auto load.

Once it has successfully loaded the plug-in you can use any commands from it.

---

*The `_ui_*` folders are used to have an isolated tested enviroment for the error und overall gui without the need to start maya.*

## Usage

#### In Mel:
<code>circlelize</code> or <code>circlelizerInterface</code>

#### In Python:

<code>import maya.cmds as cmds</code><br>
<code>cmds.circlelize()</code> or <br>
<code>cmds.circlelizerInterface()</code><br>

## Commands
It includes two commands **circlelize(...)** and **circlelizerInterface(...)** the first one is the actual tool and the second one is used for loading the graphical interface.

#### <code>circlelize</code> supports:
- **radius**, r *float* <br>
the radius of the circle
- **degree**, d *float* <br>
defines the angle of the circle (0-360°) **experimental needs a revamp**
- **midPoint**, m (*float*, *float*, *float*) <br>
defines the center of the circle
- **circleNormal**, cn (*float*, *float*, *float*) <br>
the normal which will describe the circle facing direction
- **projection**, p *bool* <br>
    projects the circle onto the mesh it was created from


#### <code>circlelizerInterface</code> supports:
- **slideInput**, si *bool* <br>
enable/disable custom widget
- **style**, s *bool* <br>
enable/disable stylesheet
- **logo**, l *bool* <br>
enable/disable logo widget

*If anyone wonders about the "__slideInput__" it is a custom widget which I have written. Everything it does is imitating the normal input from Maya where you can drag your mouse to define a number.*

**Note**: SlideInput widget does not work with 2016.5 and below!

## Supported Maya Versions
- Maya 2019 (tested)
- It should work till version Maya 2013 (Please give me a feedback on versions 2013 - 2018)

## Thanks!
LifeArtist/B4rtware
