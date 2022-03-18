# CQtoFC: CQtoFC: A module for reading CadQuery generated STEP files into FreeCAD.

## Table of Contents (alphabetical order):

* 1 Class: [FabCQtoFC](#cqtofc--fabcqtofc):
  * 1.1 [process()](#cqtofc----process): Process a JSON file into a FreeCAD documents.
  * 1.2 [node_process()](#cqtofc----node-process): Process one 'node' of JSON content.

## <a name="cqtofc--fabcqtofc"></a>1 Class FabCQtoFC:

Import CadQuery .step files into FreeCAD.

### <a name="cqtofc----process"></a>1.1 `FabCQtoFC.`process():

FabCQtoFC.process(self) -> None:

Process a JSON file into a FreeCAD documents.

### <a name="cqtofc----node-process"></a>1.2 `FabCQtoFC.`node_process():

FabCQtoFC.node_process(self, json_dict: Dict[str, Any], group: Any, indent: str = '', tracing: str = '') -> None:

Process one 'node' of JSON content.



