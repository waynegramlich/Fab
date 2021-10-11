# ApexPart: Apex interface to FreeCAD PartDesign workbench.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexNode](#apexnode)
  * 2.1 [ApexNode.configure](#apexnode-configure)

## 1 <a name="introduction"></a>Introduction


The primary class is the ApexPart class.  The preferred way to create a new part is
to subclass:

     # MyClass:
     class MyClass(ApexPart.ApexPart):
        MyClass: ...

        Attributes:
        * *Atribute1*: ...
        

      def __init__(self, name: str, parent: ApexClass, other_args...) -> None:
          Initialize MyClass.
          super().__init__(self, name, parent)

          ...


## 2 Class ApexNode <a name="apexnode"></a>

class ApexNode(object):

One node of ApexNode tree.

Attributes:
* *name* (str): The node name.
* *parent* (ApexNode): The node parent.
* *full\_path* (str):  The node full path (e.g. "root.middle1...middleN.leaf")


### 2.1 ApexNode.configure <a name="apexnode-configure"></a>

def *configure*(self) -> None:

Configure a node.

The sub-class should override this method to configure dimensions, etc.
