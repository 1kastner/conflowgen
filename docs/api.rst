API documentation
-----------------

.. automodule:: conflowgen
.. autonamedtuple:: conflowgen.ContainersAndTEUContainerFlowPair
.. autonamedtuple:: conflowgen.ContainerFlowAdjustedToVehicleType
.. autoenum:: conflowgen.ContainerLength
    :members:
.. autoenum:: conflowgen.ModeOfTransport
    :members:
.. autonamedtuple:: conflowgen.OutboundUsedAndMaximumCapacity
    :members:
.. autofunction:: conflowgen.setup_logger
.. autoenum:: conflowgen.StorageRequirement
    :members:
.. autonamedtuple:: conflowgen.TransshipmentAndHinterlandComparison


Interact with the database
==========================

.. autoclass:: conflowgen.DatabaseChooser
    :members:


Managers
========

.. autoclass:: conflowgen.ContainerLengthDistributionManager
    :members:
.. autoclass:: conflowgen.ContainerFlowGenerationManager
    :members:
.. autoclass:: conflowgen.ContainerStorageRequirementDistributionManager
    :members:
.. autoclass:: conflowgen.ExportContainerFlowManager
    :members:
.. autoclass:: conflowgen.ModeOfTransportDistributionManager
    :members:
.. autoclass:: conflowgen.PortCallManager
    :members:
.. autoclass:: conflowgen.TruckArrivalDistributionManager
    :members:


Data Outputs
============

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
.. autoclass:: conflowgen.ContainerFlowByVehicleTypePreview
    :members:
.. autoclass:: conflowgen.ContainerFlowByVehicleTypePreviewReport
    :members:
.. autonamedtuple:: conflowgen.HinterlandModalSplit
.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityAnalysis
    :members:
.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityAnalysisReport
    :members:
.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityPreview
    :members:
.. autoclass:: conflowgen.InboundAndOutboundVehicleCapacityPreviewReport
    :members:
.. autonamedtuple:: conflowgen.RequiredAndMaximumCapacityComparison
.. autoclass:: conflowgen.ModalSplitAnalysis
    :members:
.. autoclass:: conflowgen.ModalSplitAnalysisReport
    :members:
.. autoclass:: conflowgen.ModalSplitPreview
    :members:
.. autoclass:: conflowgen.ModalSplitPreviewReport
    :members:
.. autoclass:: conflowgen.QuaySideThroughputAnalysis
    :members:
.. autoclass:: conflowgen.QuaySideThroughputAnalysisReport
    :members:
.. autofunction:: conflowgen.run_all_posthoc_analyses
.. autofunction:: conflowgen.run_all_previews
.. autoclass:: conflowgen.TruckGateThroughputAnalysis
    :members:
.. autoclass:: conflowgen.TruckGateThroughputAnalysisReport
    :members:
.. autoclass:: conflowgen.VehicleCapacityExceededPreview
    :members:
.. autoclass:: conflowgen.VehicleCapacityExceededPreviewReport
    :members:
.. autoclass:: conflowgen.YardCapacityAnalysis
    :members:
.. autoclass:: conflowgen.YardCapacityAnalysisReport
    :members:


Data Export
===========

.. autoenum:: conflowgen.ExportFileFormat
    :members:

