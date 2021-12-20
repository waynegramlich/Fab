# Tree: Model tree management.

Table of Contents:
* 1 [Introduction](#introduction):
  * 1.1 [ModelNode.\_\_post\_init\_\_](#modelnode---post-init--)
  * 1.2 [ModelNode.\_setup](#modelnode--setup)
  * 1.3 [ModelNode.check](#modelnode-check)
  * 1.4 [ModelNode.configure](#modelnode-configure)
  * 1.5 [ModelNode.get\_configurations](#modelnode-get-configurations)
  * 1.6 [ModelNode.produce](#modelnode-produce)
  * 1.7 [ModelRoot.\_\_post\_init\_\_](#modelroot---post-init--)

## 1 <a name="introduction"></a>Introduction


The Tree package provides a tree of nodes that mostly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

The base class is ModelNode organized as follows:

* ModelNode: Tree node base class.
  * ModelRoot: The Root of the tree.
  * ModelGroup: A Group of ModelNode's in a tree.
    * ModelFile: A Node that corresponds to a `.fcstd` file.
    * ModelAssembly: A group of ModelAssembly's and/or ModelPart's.  (Defined in ??)
  * ModelPart: A physical part that is modeled.  (Defined in Part)
  * ModelLink: ???

The Tree enforces the following constraints:
* Each ModelNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with the character being a letter.)
* All of the children of a ModelNode must have distinct names.
* A node may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)
* The ModelRoot must be named 'Root'.

Each ModelNode has a *FullPath* property which is string that contains the ModelNode Names
from the ModelRoot downwards separated by a '.'.  The "Root." is skipped because it is redundant.
Each ModelNode has an Parent attribute that specifies the parent ModelNode

ModelNode implement

The ModelNode base class implements three recursive methods:

* configure(context) -> Tuple[str, ...]:
  Recursively propagate configuration values during the configuration phase.
  All configured values are returns a tuple of strings of the form "FULL_NAME:PROPERTY_NAME:VALUE".
* check(context) -> Tuple[str, ...]:
  Recursively checks for errors during the check phase and returns a tuple of error strings.
* build(context) -> Tuple[str, ...]:
  Recursively used to build the model and generate any production files (CNC, STL, DWG, etc.)
  Any errors and warnings are returned as a tuple of strings.

All of these methods pass a *context* dictionary from level to level.  The rule is that anything
can be added to the dictionary.  In order to prevent *context* dictionary pollution, each
level makes a shallow dictionary copy (i.e. context.copy()).

There are three phases:
* Configuration Phase:
  The configuration phase is where constraints get propagated between ModelNode's.  Each
  ModelNode recomputes its configuration values.  It can do this by reading other values
  from ModelNode's elsewhere in ModelRoot tree then computing new values.  This is done
  repeatably until no more configuration values change or until it is pretty clear that
  there is cyclic dependency will not converge.  When convergence fails, the list of
  configuration values that did not stabilize are presented.  If there are no convergence
  issues, the next phase occurs.
* Check Phase:
  The check phase recursively performs sanity checking for each ModelNode in the tree.
  The result is a list of error messages.  If the are no errors, the next phase occurs.
* Build Phase:
  The build phase recursively performs the build operations.  This includes generating
  the FreeCAD solids/assemblies and the associated output files.


### 1.1 ModelNode.\_\_post\_init\_\_ <a name="modelnode---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Finish initializing ModelNode.

### 1.2 ModelNode.\_setup <a name="modelnode--setup"></a>

def \_setup(self, *parent*:  "ModelNode", *tracing*:  *str* = "") -> None:

Recursively setup the ModelNode tree.

### 1.3 ModelNode.check <a name="modelnode-check"></a>

def *check*(self, *context*:  Dict[str, Any]) -> Tuple[str, ...]:

Check ModelNode for errors.

### 1.4 ModelNode.configure <a name="modelnode-configure"></a>

def *configure*(self, *context*:  Dict[str, Any], *tracing*:  *str* = "") -> Tuple[str, ...]:

Configure ModelNode.

### 1.5 ModelNode.get\_configurations <a name="modelnode-get-configurations"></a>

def *get\_configurations*(self, *attribute\_names*:  Tuple[str, ...]) -> Tuple[str, ...]:

Return configurations strings for named attributes.

### 1.6 ModelNode.produce <a name="modelnode-produce"></a>

def *produce*(self, *context*:  Dict[str, Any], *tracing*:  *str* = "") -> Tuple[str, ...]:

Produce ModelNode.

### 1.7 ModelRoot.\_\_post\_init\_\_ <a name="modelroot---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Process ModelRoot.
