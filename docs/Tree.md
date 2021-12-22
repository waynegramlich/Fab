# Tree: 
Tree: Model tree management.

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

## Table of Contents (alphabetical order):

* 1 Class: [ModelNode](#tree--modelnode):
  * 1.1 [check()](#tree----check): Check ModelNode for errors.
  * 1.2 [configure()](#tree----configure): Configure ModelNode.
  * 1.3 [get_configurations()](#tree----get-configurations): Return configurations strings for named attributes.
  * 1.4 [produce()](#tree----produce): Produce ModelNode.
* 2 Class: [ModelRoot](#tree--modelroot):
  * 2.1 [configure_constraints()](#tree----configure-constraints): Configure the ModelNode tree until is constraints are stable.
* 3 Class: [MyNode1](#tree--mynode1):
  * 3.1 [configure()](#tree----configure): Configure MyNode1.
* 4 Class: [MyNode2](#tree--mynode2):
  * 4.1 [configure()](#tree----configure): Configure MyNode1.
* 5 Class: [MyNode3](#tree--mynode3):
  * 5.1 [configure()](#tree----configure): Configure MyNode1.

## <a name="tree--modelnode"></a>1 Class ModelNode:

Represents one node in the tree.
Attributes:
* *Name* (str): The ModelNode name.
* *Parent* (ModelNode): The ModelNode parent.
* *ChildrenNodes* (Tuple[ModelNode, ...): The children ModelNode's.
* *FullPath* (str):  The ModelNode full path.

### <a name="tree----check"></a>1.1 `ModelNode.`check():

ModelNode.check(self, context: typing.Dict[str, typing.Any]) -> typing.Tuple[str, ...]:

Check ModelNode for errors.

### <a name="tree----configure"></a>1.2 `ModelNode.`configure():

ModelNode.configure(self, context: typing.Dict[str, typing.Any], tracing: str = '') -> typing.Tuple[str, ...]:

Configure ModelNode.

### <a name="tree----get-configurations"></a>1.3 `ModelNode.`get_configurations():

ModelNode.get_configurations(self, attribute_names: typing.Tuple[str, ...]) -> typing.Tuple[str, ...]:

Return configurations strings for named attributes.

### <a name="tree----produce"></a>1.4 `ModelNode.`produce():

ModelNode.produce(self, context: typing.Dict[str, typing.Any], tracing: str = '') -> typing.Tuple[str, ...]:

Produce ModelNode.


## <a name="tree--modelroot"></a>2 Class ModelRoot:

The Root mode a ModelNode tree.

### <a name="tree----configure-constraints"></a>2.1 `ModelRoot.`configure_constraints():

ModelRoot.configure_constraints(self, maximum_iterations: int = 20, verbosity: int = 4, tracing: str = '') -> None:

Configure the ModelNode tree until is constraints are stable.
Arguments:
* *maximum_iterations* (int): The maximum number of iterations (default: 20).
* *verbosity* (int): Verbosity level:
  0: No messages.
  1: Iteration messages only.
  N: Iteration messages with N-1 of the differences:


## <a name="tree--mynode1"></a>3 Class MyNode1:

First ModelNode.

### <a name="tree----configure"></a>3.1 `MyNode1.`configure():

MyNode1.configure(self, context: typing.Dict[str, typing.Any], tracing: str = '') -> typing.Tuple[str, ...]:

Configure MyNode1.


## <a name="tree--mynode2"></a>4 Class MyNode2:

MyNode1: First ModelNode.

### <a name="tree----configure"></a>4.1 `MyNode2.`configure():

MyNode2.configure(self, context: typing.Dict[str, typing.Any], tracing: str = '') -> typing.Tuple[str, ...]:

Configure MyNode1.


## <a name="tree--mynode3"></a>5 Class MyNode3:

MyNode1: First ModelNode.

### <a name="tree----configure"></a>5.1 `MyNode3.`configure():

MyNode3.configure(self, context: typing.Dict[str, typing.Any], tracing: str = '') -> typing.Tuple[str, ...]:

Configure MyNode1.



