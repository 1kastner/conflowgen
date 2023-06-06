API
---

Domain datatypes
================

.. autonamedtuple:: conflowgen.ContainerFlowAdjustedToVehicleType

.. autoenum:: conflowgen.ContainerLength
    :members:

.. autonamedtuple:: conflowgen.ContainerVolumeByVehicleType

.. autonamedtuple:: conflowgen.ContainerVolumeFromOriginToDestination

.. autonamedtuple:: conflowgen.HinterlandModalSplit

.. autoenum:: conflowgen.ModeOfTransport
    :members:

.. autonamedtuple:: conflowgen.OutboundUsedAndMaximumCapacity
    :members:

.. autonamedtuple:: conflowgen.RequiredAndMaximumCapacityComparison

.. autoenum:: conflowgen.StorageRequirement
    :members:

.. autonamedtuple:: conflowgen.TransshipmentAndHinterlandSplit

.. autonamedtuple:: conflowgen.VehicleIdentifier


Setting up ConFlowGen
=====================

.. autoclass:: conflowgen.DatabaseChooser
    :members:

.. autofunction:: conflowgen.setup_logger

Setting input data
==================

With the following classes, the schedules, input values and input distributions are set.
These are all required for generating the synthetic data.

.. autoclass:: conflowgen.ContainerFlowGenerationManager
    :members:

.. autoclass:: conflowgen.ContainerLengthDistributionManager
    :members:

.. autoclass:: conflowgen.StorageRequirementDistributionManager
    :members:

.. autoclass:: conflowgen.ContainerWeightDistributionManager
    :members:

.. autoclass:: conflowgen.ModeOfTransportDistributionManager
    :members:

.. autoclass:: conflowgen.ContainerDwellTimeDistributionManager
    :members:

.. autoclass:: conflowgen.PortCallManager
    :members:

.. autoclass:: conflowgen.TruckArrivalDistributionManager
    :members:


Generating previews
===================

.. autoclass:: conflowgen.ContainerFlowByVehicleTypePreview
    :members:

.. autoclass:: conflowgen.ContainerFlowByVehicleTypePreviewReport
    :members:

.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityPreview
    :members:

.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityPreviewReport
    :members:

.. autoclass:: conflowgen.ModalSplitPreview
    :members:

.. autoclass:: conflowgen.ModalSplitPreviewReport
    :members:

.. autofunction:: conflowgen.run_all_previews

.. autoclass:: conflowgen.VehicleCapacityExceededPreview
    :members:

.. autoclass:: conflowgen.VehicleCapacityUtilizationOnOutboundJourneyPreviewReport
    :members:

.. autoclass:: conflowgen.TruckGateThroughputPreview
    :members:

.. autoclass:: conflowgen.TruckGateThroughputPreviewReport
    :members:

Running analyses
================

.. autoclass:: conflowgen.ContainerDwellTimeAnalysis
    :members:

.. autoclass:: conflowgen.ContainerDwellTimeAnalysisReport
    :members:

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysis
    :members:

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysisReport
    :members:

.. autoclass:: conflowgen.ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysis
    :members:

.. autoclass:: conflowgen.ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport
    :members:

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysisSummary
    :members:

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport
    :members:

.. autoclass:: conflowgen.ContainerFlowByVehicleTypeAnalysis
    :members:

.. autoclass:: conflowgen.ContainerFlowByVehicleTypeAnalysisReport
    :members:

.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityAnalysis
    :members:

.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityAnalysisReport
    :members:

.. autoclass:: conflowgen.InboundToOutboundVehicleCapacityUtilizationAnalysis
    :members:

.. autoclass:: conflowgen.InboundToOutboundVehicleCapacityUtilizationAnalysisReport
    :members:

.. autoclass:: conflowgen.ModalSplitAnalysis
    :members:

.. autoclass:: conflowgen.ModalSplitAnalysisReport
    :members:

.. autoclass:: conflowgen.QuaySideThroughputAnalysis
    :members:

.. autoclass:: conflowgen.QuaySideThroughputAnalysisReport
    :members:

.. autofunction:: conflowgen.run_all_analyses

.. autoclass:: conflowgen.TruckGateThroughputAnalysis
    :members:

.. autoclass:: conflowgen.TruckGateThroughputAnalysisReport
    :members:

.. autoclass:: conflowgen.YardCapacityAnalysis
    :members:

.. autoclass:: conflowgen.YardCapacityAnalysisReport
    :members:

Using distributions
===================

Most of the distributions in ConFlowGen are discrete distributions and are just reflected by classic Python
dictionaries where the key refers to the element to be drawn and the value is the probability.
In some cases, such as container dwell times, continuous distributions are required.

.. autoclass:: conflowgen.ContinuousDistribution
    :members:

.. autoclass:: conflowgen.ContainerDwellTimeDistributionInterface
    :members:

Working with reports
====================

When working with :func:`.run_all_previews` or :func:`.run_all_analyses`, there is some common functionality.
If you wish to add another markup language besides plaintext and markdown for these two lists of reports,
you can define them here and pass them as parameters to the aforementioned functions.

.. autoclass:: conflowgen.DisplayAsMarkdown
    :members:

.. autoclass:: conflowgen.DisplayAsMarkupLanguage
    :members:

.. autoclass:: conflowgen.DisplayAsPlainText
    :members:

.. autoclass:: conflowgen.DataSummariesCache
    :members:

Exporting data
==============

.. autoclass:: conflowgen.ExportContainerFlowManager
    :members:

.. autoenum:: conflowgen.ExportFileFormat
    :members:
