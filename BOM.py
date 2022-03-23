#!/usr/bin/env python3
"""ApexBOM: Bill of Materials (i.e. BOM) and ordering information.

The general idea is that a project is assembled from both raw materials and manufactured parts
that are created in factories.  These factory parts/materials are frequently redistributed to
intermediate vendors that you can actual obtains the desired parts from.
The overall concept is called a Bill Of Materials (i.e. BOM) and it is a surprisingly complex topic.
Eventually, the FreeCAD community will decide what to do with about Bill of Materials management.
Until then, the following place ApexBOM place holder classes are used.

Classes:
* ApexBOM: An actual specific bill of materials for given project.
* oApexCollection: A collection (e.g. catalog) of parts from vendors/manufacturers.
* ApexDetail: Information about a specific part.
* ApexFactory: A factory (i.e. manufacturer) that constructs parts.
* ApexFactoryDetail: Factory specific information about a specific part.
* ApexVendor: A vendor that sells parts to end-users.
* ApexVendorOrder: An order for parts from a Vendor.
* ApexVendorDetail: Vendor specific information about a specific part.

"""

import sys
sys.path.append(".")
import Embed
Embed.setup()


from dataclasses import dataclass
from typing import Tuple


# ApexDetail:
class ApexDetail(object):
    """ApexDetail: More inromation about the object."""
    pass


# ApexVendorDetail:
class ApexVendorDetail(ApexDetail):
    """ApexVendorDetail: More Vendor information."""
    pass


# ApexBom:
@dataclass
class ApexBOM(object):
    """ApexBOM: A Bill of Materials for a project."""

    parts: Tuple[ApexDetail, ...]  # Information about the


# ApexCollection:
@dataclass
class ApexCollection(dict):
    """ApexCollection: A collection (e.g. catalog) of parts."""

    # https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict


# ApexFactory:
@dataclass
class ApexFactory:
    """Information about a factory."""
    name: str
    address: Tuple[str, ...]


# ApexFactoryDetail


# ApexVendor:
class ApexVendor:
    """Information about a vendor."""
    name: str
    address: Tuple[str, ...]


# ApexVendorOrder:
@dataclass
class ApexVendorOrder:
    """ApexVendorOrder: An order for parts."""
    details: Tuple[ApexVendorDetail, ...]


# ApexVendorDetail:
@dataclass
class ApexVendorDetail:
    """ApexVendorDetail: A vendor item detail."""
    vendor_number: int  # The required number to order
    key: str  # The Vendor part number
    description: str  # The vendor part description
    price: float  # The vendor price.

# <--------------------------------------- 100 characters ---------------------------------------> #
