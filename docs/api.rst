API documentation
-----------------

.. automodule:: conflowgen


Domain datatypes
================

.. autonamedtuple:: conflowgen.ContainerFlowAdjustedToVehicleType

.. autoenum:: conflowgen.ContainerLength
    :members:

.. autonamedtuple:: conflowgen.ContainersAndTEUContainerFlowPair

.. autonamedtuple:: conflowgen.HinterlandModalSplit

.. autoenum:: conflowgen.ModeOfTransport
    :members:

.. autonamedtuple:: conflowgen.OutboundUsedAndMaximumCapacity
    :members:

.. autonamedtuple:: conflowgen.RequiredAndMaximumCapacityComparison

.. autoenum:: conflowgen.StorageRequirement
    :members:

.. autonamedtuple:: conflowgen.TransshipmentAndHinterlandComparison


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

.. autoclass:: conflowgen.ContainerStorageRequirementDistributionManager
    :members:

.. autoclass:: conflowgen.ContainerWeightDistributionManager
    :members:

.. autoclass:: conflowgen.ModeOfTransportDistributionManager
    :members:

.. autoclass:: conflowgen.PortCallManager
    :members:

.. autoclass:: conflowgen.TruckArrivalDistributionManager
    :members:


Getting previews
================

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

.. autoclass:: conflowgen.VehicleCapacityExceededPreviewReport
    :members:

Getting analyses
================

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysis
    :members:

.. autoclass:: conflowgen.ContainerFlowAdjustmentByVehicleTypeAnalysisReport
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

Working with reports
====================

When working with :func:`.run_all_previews` or :func:`.run_all_analyses`, there is some common functionality.

.. autoclass:: conflowgen.DisplayAsMarkdown
    :members:

.. autoclass:: conflowgen.DisplayAsMarkupLanguage
    :members:

.. autoclass:: conflowgen.DisplayAsPlainText
    :members:

Exporting data
==============

.. autoclass:: conflowgen.ExportContainerFlowManager
    :members:

.. autoenum:: conflowgen.ExportFileFormat
    :members:
