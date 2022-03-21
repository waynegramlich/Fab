# BOM: ApexBOM: Bill of Materials (i.e. BOM) and ordering information.
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

## Table of Contents (alphabetical order):

* 1 Class: [ApexBOM](#bom--apexbom):
* 2 Class: [ApexCollection](#bom--apexcollection):
* 3 Class: [ApexDetail](#bom--apexdetail):
* 4 Class: [ApexFactory](#bom--apexfactory):
* 5 Class: [ApexVendor](#bom--apexvendor):
* 6 Class: [ApexVendorDetail](#bom--apexvendordetail):
* 7 Class: [ApexVendorOrder](#bom--apexvendororder):

## <a name="bom--apexbom"></a>1 Class ApexBOM:

A Bill of Materials for a project.


## <a name="bom--apexcollection"></a>2 Class ApexCollection:

A collection (e.g. catalog) of parts.


## <a name="bom--apexdetail"></a>3 Class ApexDetail:

More inromation about the object.


## <a name="bom--apexfactory"></a>4 Class ApexFactory:

Information about a factory.


## <a name="bom--apexvendor"></a>5 Class ApexVendor:

Information about a vendor.


## <a name="bom--apexvendordetail"></a>6 Class ApexVendorDetail:

A vendor item detail.


## <a name="bom--apexvendororder"></a>7 Class ApexVendorOrder:

An order for parts.



