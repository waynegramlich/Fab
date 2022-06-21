# FabToolBits: FabToolBits: Toop Bit classes.
This module provides one class for each different kind of supported tool bit.
Instatiations of these tool bits live in the `.../Tools/Bit/` directory with a suffix of `.fctb`.
Each of the classes below is a sub-class of the FabBit class defined in the FabToolTemplates module.

The classes are:
  * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
  * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
  * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
  * FabDoveTailBit: This corresponds to `Tools/Shape/dovetail.fcstd`.
  * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
  * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
  * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
  * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
  * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.
  * FabVBit: This corresponds to `Tools/Shape/v-bit.fcstd`.

The FabBit sub-class defines the following 4 attributes which is present in every FabBit sub-class:
  * *Name* (str): The name of Ball End bit.
  * *BitFile* (PathFile): The `.fctb` file.
  * *Shape* (FabShape): The associated `.fcstd` shape.
  * *Attributes* (FabAttributes): Any associated attributes.
Both FabShape and FabAttributes are also defined in the FabTemplates module as well.

## Table of Contents (alphabetical order):

* 1 Class: [FabBallEndBit](#fabtoolbits--fabballendbit):
  * 1.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabBallEndBit.
* 2 Class: [FabBullNoseBit](#fabtoolbits--fabbullnosebit):
  * 2.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabBullNoseBit.
* 3 Class: [FabChamferBit](#fabtoolbits--fabchamferbit):
  * 3.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabChamferBit.
* 4 Class: [FabDoveTailBit](#fabtoolbits--fabdovetailbit):
  * 4.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabDoveTailBit.
* 5 Class: [FabDrillBit](#fabtoolbits--fabdrillbit):
  * 5.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabDrillBit.
  * 5.2 [getBitPriority()](#fabtoolbits----getbitpriority): Return operation priority for a FabEndMillBit.
* 6 Class: [FabEndMillBit](#fabtoolbits--fabendmillbit):
  * 6.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabEndMillBit.
  * 6.2 [getBitPriority()](#fabtoolbits----getbitpriority): Return operation priority for a FabEndMillBit.
* 7 Class: [FabProbeBit](#fabtoolbits--fabprobebit):
  * 7.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabProbeBit.
* 8 Class: [FabSlittingSawBit](#fabtoolbits--fabslittingsawbit):
  * 8.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabSlittingSawBit.
* 9 Class: [FabThreadMillBit](#fabtoolbits--fabthreadmillbit):
  * 9.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabVBit.
  * 9.2 [getBitPriority()](#fabtoolbits----getbitpriority): Return operation priority for a FabEndThreadMillBit.
* 10 Class: [FabVBit](#fabtoolbits--fabvbit):
  * 10.1 [getOperationKinds()](#fabtoolbits----getoperationkinds): Return the kind of operations by a FabVBit.
  * 10.2 [getBitPriority()](#fabtoolbits----getbitpriority): Return operation priority for a FabEndMillBit.

## <a name="fabtoolbits--fabballendbit"></a>1 Class FabBallEndBit:

An ball end bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitStem* (str): The stem of the ball end `.fctb` file name.
* *ShapeStem* (str): The stem of the associated ball end `.fcstd` shape (e.g. "ballend".)
* *Attributes* (FabAttributes): Any associated ball end attributes.
* *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
* *Diameter* (Union[str, float]): The ball end cutter diameter.
* *Length* (Union[str, float]): The total length of the ball end.
* *ShankDiameter: (Union[str, float]): The ball end shank diameter.

Constructor:
* FabBallEndBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>1.1 `FabBallEndBit.`getOperationKinds():

FabBallEndBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabBallEndBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabbullnosebit"></a>2 Class FabBullNoseBit:

An bull nose bit template.
Attributes:
* *Name* (str): The name of Bull Nose bit.
* *BitStem* (str): The stem of the bull nose `.fctb` file.
* *ShapeStem* (str): The stem of associated bull nose `.fcstd` shape (e.g. "bullnose".)
* *Attributes* (FabAttributes): Any associated bull nose attributes.
* *CuttingEdgeHeight* (Union[str, float]): The bull nose cutting edge height.
* *Diameter* (Union[str, float]): The bull nose cutter diameter.
* *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
* *Length* (Union[str, float]): The total length of the bull nose cutter.
* *ShankDiameter: (Union[str, float]): The bull nose shank diameter.

Constructor:
* FabBullNoseBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>2.1 `FabBullNoseBit.`getOperationKinds():

FabBullNoseBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabBullNoseBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabchamferbit"></a>3 Class FabChamferBit:

An chamfer bit template.
Attributes:
* *Name* (str): The name of Chamfer bit.
* *BitStem* (str): The stem of chamfer`.fctb` file name.
* *ShapeStem* (str): The stem of associated chamfer `.fcstd` shape (e.g. "chamfer".)
* *Attributes* (FabAttributes): Any associated chamfer bit attributes.
* *CuttingEdgeAngle* (Union[str, float]): The chamfer bit cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The chamfer bit cutting edge height.
* *Diameter* (Union[str, float]): The chamfer bit outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer bit.
* *ShankDiameter: (Union[str, float]): The chamfer bit shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer bit.

Constructor:
* FabChamferBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>3.1 `FabChamferBit.`getOperationKinds():

FabChamferBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabChamferBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabdovetailbit"></a>4 Class FabDoveTailBit:

An dove tail bit template.
Attributes:
* *Name* (str): The name of dove tail bit.
* *BitStem* (str): The stem of dove tail `.fctb` file.
* *ShapeStem* (str): The stem associated dove tail `.fcstd` shape (e.g. "dovetail".)
* *Attributes* (FabAttributes): Any associated dove tail attributes.
* *CuttingEdgeAngle* (Union[str, float]): The dove tail cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The dove tale cutting edge height.
* *Diameter* (Union[str, float]): The dove tail outer diameter.
* *Length* (Union[str, float]): The dove tail total length.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the dove tail and shank.
* *NeckHeight* (Union[str, float]):
   The height of the neck between the dove tail cutter and shank.
* *ShankDiameter: (Union[str, float]): The dove tail shank diameter.
* *TipDiameter* (Union[str, float]):
  In theory, tip diameter of the dove tail.  In practice, *Diameter* is what is actually used.

Constructor:
* FabDoveTailBit("Name", "BitStem", "ShapeStem", Attributes, CuttingEdgeAngle,
  CuttingEdgeHeight, Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>4.1 `FabDoveTailBit.`getOperationKinds():

FabDoveTailBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabDoveTailBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabdrillbit"></a>5 Class FabDrillBit:

An drill bit template.
Attributes:
* *Name* (str): The name of drill bit.
* *BitStem* (str): The stem of drill bit `.fctb` file.
* *ShapeStem* (str): The stem of associated drill bit `.fcstd` shape (e.g. "drill".)
* *Attributes* (FabAttributes): Any associated drill bit attributes.
* *Diameter* (Union[str, float]): The drill bit outer diameter.
* *Length* (Union[str, float]): The total length of the drill bit.
* *TipAngle: (Union[str, float]): The drill bit tip point angle.

Constructor:
* FabDrillBit("Name", "BitStem", "ShapeStem", Attributes, Diameter, Length, TipAngle)

### <a name="fabtoolbits----getoperationkinds"></a>5.1 `FabDrillBit.`getOperationKinds():

FabDrillBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabDrillBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)

### <a name="fabtoolbits----getbitpriority"></a>5.2 `FabDrillBit.`getBitPriority():

FabDrillBit.getBitPriority(self, operation_kind: str, depth: float, tracing: str = '') -> Union[float, NoneType]:

Return operation priority for a FabEndMillBit.
Arguments:
* *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
* *depth* (str): Depth of drill operation.

Returns:
* (Optional[float]): The priority as a negative number, where more negative numbers
  have a higher priority.  None is returned if there is bit does not support either
  the operation kind or depth.


## <a name="fabtoolbits--fabendmillbit"></a>6 Class FabEndMillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of end mill bit.
* *BitStem* (str): The stem of the end mill `.fctb` file.
* *ShapeStem* (str): The stem of the associated end mill `.fcstd` shape (e.g. "endmill".)
* *Attributes* (FabAttributes): Any associated end mill attributes.
* *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The end mill shank diameter.

Constructor:
* FabEndMillBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>6.1 `FabEndMillBit.`getOperationKinds():

FabEndMillBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabEndMillBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)

### <a name="fabtoolbits----getbitpriority"></a>6.2 `FabEndMillBit.`getBitPriority():

FabEndMillBit.getBitPriority(self, operation_kind: str, depth: float, tracing: str = '') -> Union[float, NoneType]:

Return operation priority for a FabEndMillBit.
Arguments:
* *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
* *depth* (str):
  Depth of end-mill operation or 0.0 for a "generic" priority independent of depth.

Returns:
* (Optional[float]): The priority as a negative number, where more negative numbers
  have a higher priority.  None is returned if there is bit does not support either
  the *operation_kind* or *depth*.


## <a name="fabtoolbits--fabprobebit"></a>7 Class FabProbeBit:

A probe bit template.
Attributes:
* *Name* (str): The name of probe bit.
* *BitStem* (str): The stem of the probe `.fctb` file.
* *ShapeStem* (str): The stem of the associated probe `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated probe attributes.
* *Diameter* (Union[str, float]): The probe ball diameter.
* *Length* (Union[str, float]): The total length of the probe.
* *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

Constructor:
* FabProbeBit("Name", "BitStem", "ShapeStem", Attributes, Diameter, Length, ShaftDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>7.1 `FabProbeBit.`getOperationKinds():

FabProbeBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabProbeBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabslittingsawbit"></a>8 Class FabSlittingSawBit:

An slitting saw bit.
Attributes:
* *Name* (str): The name of slitting saw bit.
* *BitStem* (str): The stem of slitting saw `.fctb` file.
* *ShapeStem* (str):
  The stem of the associated slitting saw `.fcstd` shape (e.g. "slittingsaw".)
* *Attributes* (FabAttributes): Any associated slitting saw attributes.
* *BladeThickness* (Union[str, float]): The slitting saw blade thickness.
* *CapDiameter* (Union[str, float]): The slitting saw end cab diameter.
* *CapHeight* (Union[str, float]): The slitting end end cab height.
* *Diameter* (Union[str, float]): The slitting saw blade diameter.
* *Length* (Union[str, float]): The length of the slitting saw.
* *ShankDiameter: (Union[str, float]): The slitting saw shank diameter.

Constructor:
* FabSlittingSawBit("Name", "BitStem", "ShapeStem", Attributes,
  BladeThickness, CapDiameter, CapHeight, Diameter, Length, ShankDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>8.1 `FabSlittingSawBit.`getOperationKinds():

FabSlittingSawBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabSlittingSawBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)


## <a name="fabtoolbits--fabthreadmillbit"></a>9 Class FabThreadMillBit:

An thread mill bit template.
Attributes:
* *Name* (str): The name of thread mill bit.
* *BitStem* (str): The stem of thread mill `.fctb` file.
* *ShapeStem* (str): The stem of the associated thread mill `.fcstd` shape (e.g. .
* *Attributes* (FabAttributes): Any associated thread mill attributes.
* *CuttingAngle* (Union[str, float]): The thread mill point angle.
* *Crest* (Union[str, float]): The thread mill crest thickness.
* *Diameter* (Union[str, float]): The thread mill outer diameter.
* *Length* (Union[str, float]): The total length of the thread mill cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The thread mill shank diameter.

Constructor:
* FabThreadMillBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingAngle, Crest, Diameter, Length, NeckDiameter, NeckLength, ShankDiameter)

### <a name="fabtoolbits----getoperationkinds"></a>9.1 `FabThreadMillBit.`getOperationKinds():

FabThreadMillBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabVBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)

### <a name="fabtoolbits----getbitpriority"></a>9.2 `FabThreadMillBit.`getBitPriority():

FabThreadMillBit.getBitPriority(self, operation_kind: str, depth: float, tracing: str = '') -> Union[float, NoneType]:

Return operation priority for a FabEndThreadMillBit.
Arguments:
* *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
* *depth* (str): Depth of drill operation.

Returns:
* (Optional[float]): The priority as a negative number, where more negative numbers
  have a higher priority.  None is returned if there is bit does not support either
  the operation kind or depth.


## <a name="fabtoolbits--fabvbit"></a>10 Class FabVBit:

An V bit template.
Attributes:
* *Name* (str): The name of V bit.
* *BitStem* (str): The stem of V bit `.fctb` file.
* *ShapeStem* (str): The stem of the associated V bit `.fcstd` shape (e.g. "v-bit".)
* *Attributes* (FabAttributes): Any associated V bit  attributes.
* *CuttingEdgeAngle* (Union[str, float]): The V bit cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The V bit cutting edge height.
* *Diameter* (Union[str, float]): The V bit outer diameter.
* *Length* (Union[str, float]): The total length of the V bit.
* *ShankDiameter: (Union[str, float]): The V bit shank diameter.
* *TipDiameter* (Union[str, float]): The tip diameter of the V bit

Computed Attributes:
* *AngleCuttingEdgeHeight* (float): The angled cutting edge height.
* *VerticalCuttingEdgeHeight* (float): The angled cutting edge height.

Constructor:
* FabVBit("Name", "BitStem", "ShapeStem", Attributes,
  CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)

Crude ASCII bit diagram:
```
           |                       |
           |<--------- D --------->|
           |                       |
           |    +*************+ <--+-------------
           |    *             *    |          ^
           |    *             *    |          |
           |    *             *    |          |
           |    *             *    |          |
                *             *               |
     ----- +****+             +****+ -------  |
       ^   *                       *    ^     |
       |   *                       *    |     |
       |   *                       *   VCEH   |
       |   *                       *    |     |
       |   *                       *    v     |
       |   +             A.........B -------  L
      CEH   *            .        *     ^     |
       |     *           .       *      |     |
       |      *                 *       |     |
       |       *<--<CEA--+---->*        |     |
       |        *        .    *        ACEH   |
       |         *       .   *          |     |
       |          *      .  *           |     |
       |           *     . *            |     |
       v            *     *             v     v
     --------------- +***C ----------------------

                     |   |
              TD --->|   |<---
                     |   |

    D = Diameter Diameter
    CEH = Cutting Edge Height
    VCEH = Vertical Cutting Edge Height
    ACEH = Angle Cutting Edge Height (computed from CEA, D
    TD = Tip Diameter
    <CEA = Cutting Edge Angle (i.e. the point angle)
    L = Length (i.e. OAL = Overall Length)
    A/B/C = Points on right triangle where |AC|=ACEH and |AB|=(D-TD)/2
```

### <a name="fabtoolbits----getoperationkinds"></a>10.1 `FabVBit.`getOperationKinds():

FabVBit.getOperationKinds(self) -> Tuple[str, ...]:

Return the kind of operations by a FabVBit.
Returns:
* (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)

### <a name="fabtoolbits----getbitpriority"></a>10.2 `FabVBit.`getBitPriority():

FabVBit.getBitPriority(self, operation_kind: str, depth: float, tracing: str = '') -> Union[float, NoneType]:

Return operation priority for a FabEndMillBit.
Arguments:
* *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
* *depth* (str): Depth of drill operation.

Returns:
* (Optional[float]): The priority as a negative number, where more negative numbers
  have a higher priority.  None is returned if there is bit does not support either
  the operation kind or depth.



