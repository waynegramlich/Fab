# ApexPart: Apex interface to FreeCAD PartDesign workbench.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexContext](#apexcontext)
* 3 [Class ApexNode](#apexnode)
  * 3.1 [ApexNode.build](#apexnode-build)
  * 3.2 [ApexNode.configure](#apexnode-configure)
  * 3.3 [ApexNode.configure\_and\_build](#apexnode-configure-and-build)

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

      def configure(self) -> None:
          Configure MyClass.
          ...

      def build(self) -> None:
          Build MyClass.
          ...


## 2 Class ApexContext <a name="apexcontext"></a>

class ApexContext:

Build context object for controlling build.

Attributes:
* *foo*: foo.


## 3 Class ApexNode <a name="apexnode"></a>

class ApexNode(object):

One node of ApexNode tree.

Attributes:
* *name* (str): The node name.
* *parent* (ApexNode): The node parent.
* *full\_path* (str):  The node full path (e.g. "root.middle1...middleN.leaf")


### 3.1 ApexNode.build <a name="apexnode-build"></a>

def *build*(self, *context*:  ApexContext) -> None:

Build an ApexNode.

* Arguments:
  * *context* (ApexContext): The context information for the entire build.

The sub-class should override this method to build the node.

### 3.2 ApexNode.configure <a name="apexnode-configure"></a>

def *configure*(self) -> None:

Configure an ApexNode.

The sub-class should override this method to configure dimensions, etc.

### 3.3 ApexNode.configure\_and\_build <a name="apexnode-configure-and-build"></a>

def *configure\_and\_build*(self, *count*:  *int* = 25, *tracing*:  *str* = "") -> None:

Recursively configure and build the entire ApexNode tree.

* Arguments:
  *count* (int): The maximum number of configuration iterations:
