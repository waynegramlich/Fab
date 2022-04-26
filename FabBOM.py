#!/usr/bin/env python3
"""FabBOM: Bill of Materials (i.e. BOM) and ordering information.

The general idea is that a project is assembled from both raw materials and manufactured parts
that are created in factories.  These factory parts/materials are frequently redistributed to
intermediate vendors that you can actual obtains the desired parts from.
The overall concept is called a Bill Of Materials (i.e. BOM) and it is a surprisingly complex topic.
Eventually, the FreeCAD community will decide what to do with about Bill of Materials management.
Until then, the following place FabBOM place holder classes are used.

Classes:
* FabBOM: An actual specific bill of materials for given project.
* oFabCollection: A collection (e.g. catalog) of parts from vendors/manufacturers.
* FabDetail: Information about a specific part.
* FabFactory: A factory (i.e. manufacturer) that constructs parts.
* FabFactoryDetail: Factory specific information about a specific part.
* FabVendor: A vendor that sells parts to end-users.
* FabVendorOrder: An order for parts from a Vendor.
* FabVendorDetail: Vendor specific information about a specific part.

"""
# <--------------------------------------- 100 characters ---------------------------------------> #


from dataclasses import dataclass
from typing import Tuple


# FabDetail:
class FabDetail(object):
    """FabDetail: More inromation about the object."""
    pass


# FabBom:
@dataclass
class FabBOM(object):
    """FabBOM: A Bill of Materials for a project."""

    parts: Tuple[FabDetail, ...]  # Information about the


# FabCollection:
@dataclass
class FabCollection(dict):
    """FabCollection: A collection (e.g. catalog) of parts."""

    # https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict


# FabFactory:
@dataclass
class FabFactory:
    """Information about a factory."""
    name: str
    address: Tuple[str, ...]


# FabFactoryDetail


# FabVendor:
class FabVendor:
    """Information about a vendor."""
    name: str
    address: Tuple[str, ...]


# FabVendorDetail:
@dataclass
class FabVendorDetail:
    """FabVendorDetail: A vendor item detail."""
    vendor_number: int  # The required number to order
    key: str  # The Vendor part number
    description: str  # The vendor part description
    price: float  # The vendor price.


# FabVendorOrder:
@dataclass
class FabVendorOrder:
    """FabVendorOrder: An order for parts."""
    details: Tuple[FabVendorDetail, ...]


# _unit_tests():
def _unit_tests() -> None:
    """Unit tests."""
    pass


# main():
def main() -> None:
    """main program."""
    _unit_tests()


if __name__ == "__main__":
    main()
