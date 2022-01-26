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

Interacting with the database
=============================

.. autoclass:: conflowgen.DatabaseChooser
    :members:

Setting input data
==================

.. autofunction:: conflowgen.setup_logger

.. autoclass:: conflowgen.ContainerLengthDistributionManager
    :members:

.. autoclass:: conflowgen.ContainerStorageRequirementDistributionManager
    :members:

.. autoclass:: conflowgen.ModeOfTransportDistributionManager
    :members:

.. autoclass:: conflowgen.PortCallManager
    :members:

.. autoclass:: conflowgen.TruckArrivalDistributionManager
    :members:

.. autoclass:: conflowgen.ContainerFlowGenerationManager
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

.. autofunction:: conflowgen.run_all_posthoc_analyses

.. autoclass:: conflowgen.TruckGateThroughputAnalysis
    :members:

.. autoclass:: conflowgen.TruckGateThroughputAnalysisReport
    :members:

.. autoclass:: conflowgen.YardCapacityAnalysis
    :members:

.. autoclass:: conflowgen.YardCapacityAnalysisReport
    :members:

Exporting data
==============

.. autoclass:: conflowgen.ExportContainerFlowManager
    :members:

.. autoenum:: conflowgen.ExportFileFormat
    :members:
