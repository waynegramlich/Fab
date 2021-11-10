# ApexExampleBox: Example Box.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexEnclosure](#apexenclosure)
* 3 [Class Block](#block)
  * 3.1 [Block.\_\_init\_\_](#block---init--)
  * 3.2 [Block.build](#block-build)
  * 3.3 [Block.configure](#block-configure)

## 1 <a name="introduction"></a>Introduction


Builds a box of given the length, width, height and material thickness.

## 2 Class ApexEnclosure <a name="apexenclosure"></a>

class ApexEnclosure(ApexNode):

ApexEnclosure: Build a box.

Builds a box given a length, width, height, material, thickness and position in space.

Attributes:
* *dx* (ApexLength): length in X direction.
* *dy* (ApexLength): width in Y direction.
* *dz* (ApexLength): height in Z direction.
* *material* (ApexMaterial): Material to use.
* *dw* (ApexLength): material thickness.
* *center*: (ApexPoint): Center of box:
* *z\_align*: (ApexPoint): Axis to align with +Z axis.
* *y\_align: (ApexPoint): Axis to align with +Y axis.


## 3 Class Block <a name="block"></a>

class Block(ApexNode):

Block: A rectangular block.

### 3.1 Block.\_\_init\_\_ <a name="block---init--"></a>

def \_\_init\_\_(self, *name*:  *str*, *parent*:  ApexNode, *tne*:  Vector, *bsw*:  Vector, *top\_face*:  Vector, *north\_face*:  Vector, *color*:  *str* = "", *tracing*:  *str* = "") -> None:

Initlialze a Block.

* Arguments:
  * *name* (str): The name of the Block.
  * *parent* (str): The parent ApexNode.
  * *tne* (Vector): The Top-North-East corner.
  * *bsw* (Vector): The Bottom-South-West corner.
  * *top\_face* (Vector): The face to have pointing +Z when doing operations.
  * *north\_face* (Vector): The face to have pointing +Y when doing operations.
  * *color*: (str): The SVG color name to use for coloring purposes.

### 3.2 Block.build <a name="block-build"></a>

def *build*(self, *context*:  ApexContext, *tracing*:  *str* = "") -> None:

Build a Block.

* Arguments:
  *context* (ApexContext):  The context to use during building.

### 3.3 Block.configure <a name="block-configure"></a>

def *configure*(self):

Configure a Block.
