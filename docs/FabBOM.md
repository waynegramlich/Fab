# FabBOM: FabBOM: Bill of Materials (i.e. BOM) and ordering information.
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

## Table of Contents (alphabetical order):

* 1 Class: [FabBOM](#fabbom--fabbom):
* 2 Class: [FabCollection](#fabbom--fabcollection):
* 3 Class: [FabDetail](#fabbom--fabdetail):
* 4 Class: [FabFactory](#fabbom--fabfactory):
* 5 Class: [FabVendor](#fabbom--fabvendor):
* 6 Class: [FabVendorDetail](#fabbom--fabvendordetail):
* 7 Class: [FabVendorOrder](#fabbom--fabvendororder):

## <a name="fabbom--fabbom"></a>1 Class FabBOM:

A Bill of Materials for a project.


## <a name="fabbom--fabcollection"></a>2 Class FabCollection:

A collection (e.g. catalog) of parts.


## <a name="fabbom--fabdetail"></a>3 Class FabDetail:

More inromation about the object.


## <a name="fabbom--fabfactory"></a>4 Class FabFactory:

Information about a factory.


## <a name="fabbom--fabvendor"></a>5 Class FabVendor:

Information about a vendor.


## <a name="fabbom--fabvendordetail"></a>6 Class FabVendorDetail:

A vendor item detail.


## <a name="fabbom--fabvendororder"></a>7 Class FabVendorOrder:

An order for parts.



