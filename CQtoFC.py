#!/usr/bin/env python3
"""CQtoFC: A module for reading CadQuery generated STEP files into FreeCAD."""

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
USE_FREECAD, USE_CAD_QUERY = Embed.setup()

assert USE_FREECAD, "Not in FreeCAD mode"
import FreeCAD  # type: ignore
import FreeCAD as App  # type: ignore
from pathlib import Path

if App.GuiUp:
    from FreeCAD import ImportGui as FCImport
else:
    from FreeCAD import Import as FCImport


import json
from typing import Any, cast, List, Dict, IO, Tuple
from dataclasses import dataclass, field

# FabCQtoFC:
@dataclass
class FabCQtoFC(object):
    """FabCQtoFC: Import CadQuery .step files into FreeCAD."""

    json_path: Path
    steps_document: Any = field(init=False, repr=False)
    project_document: Any = field(init=False, repr=False)
    all_documents: List[Any] = field(init=False, repr=False)
    pending_links: List[Tuple[Any, Any]] = field(init=False, repr=False)

    # FabCQtoFC.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabCQtoFC."""
        assert isinstance(self.json_path, Path), self.json_path
        self.steps_document = None
        self.all_documents = []
        self.pending_links = []
        self.pending_links: List[Tuple[Any, Any]] = []
        self.project_document = None

    # FabCQtoFC.process():
    def process(self) -> None:
        """Process a JSON file into a FreeCAD documents."""
        # Create the *steps_document*:
        json_directory: Path = self.json_path.parent
        steps_document: Any = App.newDocument("Step_Files")
        self.steps_document = steps_document
        self.all_documents.append(steps_document)

        # Read in *json_path*:
        json_file: IO[str]
        json_text: str = ""
        assert self.json_path.suffix == ".json", self.json_path
        with open(self.json_path, "r") as json_file:
            json_text = json_file.read()
        json_root = cast(Dict[str, Any], json.loads(json_text))
        assert isinstance(json_root, dict), json_root

        # Recursively walk the tree starting at *json_root*:
        self.node_process(json_root, group=None, indent="  ", tracing="  ")

        # Save *all_documents*:
        document: Any
        for document in self.all_documents:
            save_path: Path = json_directory / f"{document.Label}.FCStd"
            if save_path.exists():
                save_path.unlink()
            document.saveAs(str(save_path))

        # Install all of the *pending_links*:
        pending_link: Tuple[Any, Any]
        link: Any
        part: Any
        for link, part in self.pending_links:
            link.setLink(part)

    # FabCQtoFC.node_process():
    def node_process(self, json_dict: Dict[str, Any], group: Any,
                     indent: str = "", tracing: str = "") -> None:
        """Process one 'node' of JSON content."""
        # Set up *tracing* and pretty print *indent*:
        next_tracing: str = tracing + "  " if tracing else ""
        next_indent = indent + "  " if indent else ""
        if tracing:
            print(f"{tracing}=>FabCQtoFC.child_process(*, '{indent}')")

        # Do some sanity checking:
        assert isinstance(json_dict, dict), json_dict
        kind = cast(str, json_dict["Kind"])
        label = cast(str, json_dict["Label"])
        assert isinstance(kind, str) and kind in ("Project", "Document", "Assembly", "Solid"), kind
        assert isinstance(label, str), label
        if indent:
            print(f"{indent}{label}:")
            print(f"{indent} kind: {kind}")
        steps_document: Any = self.steps_document
        project_document: Any = self.project_document

        if kind == "Project":
            pass
        elif kind == "Document":
            project_document = App.newDocument(label)
            project_document.Label = label
            self.project_document = project_document
            self.all_documents.append(project_document)
        elif kind == "Assembly":
            if group:
                group = group.newObject("App::DocumentObjectGroup", label)
            else:
                group = project_document.addObject("App::DocumentObjectGroup", label)
        elif kind == "Solid":
            step: str = cast(str, json_dict["Step"])
            assert isinstance(step, str), step
            if indent:
                print(f"{indent} step: '{step}'")
            before_size: int = len(steps_document.RootObjects)
            FCImport.insert(step, steps_document.Label)
            after_size: int = len(steps_document.RootObjects)
            assert before_size + 1 == after_size, (before_size, after_size)
            part: Any = steps_document.getObject(label)
            part.Label = f"{label}_Step"
            steps_document.RootObjects[before_size].Label = label

            # Install *link* into *group*.  Complete the link later on using *pending_links*:
            link: Any = group.newObject("App::Link", label)
            self.pending_links.append((link, part))
        else:
            assert False, kind
        self.group = group

        if "children" in json_dict:
            children = cast(List[List[Any]], json_dict["children"])
            if indent:
                print(f"{indent} children ({len(children)}):")
            assert isinstance(children, list), children

            child: Any
            for child in children:
                assert isinstance(child, list), child
                child_name = cast(str, child[0])
                child_dict = cast(Dict[str, Any], child[1])
                assert isinstance(child_name, str), child_name
                assert isinstance(child_dict, dict), child_dict
                self.node_process(child_dict, group, indent=next_indent, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabCQtoFC.child_process(*, '{indent}')")


# main():
def main() -> None:
    """The main program."""
    print("Hello")

    json_reader: FabCQtoFC = FabCQtoFC(Path("/tmp/TestProject.json"))
    json_reader.process()


if __name__ == "__main__":
    main()
