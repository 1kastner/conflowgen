Demo Script - Step by Step Guide
--------------------------------

.. _prerequisites:

Prerequisites
=============

To start, we first import the required classes, enums, and functions from ConFlowGen:

.. code-block:: python

    from conflowgen import ContainerFlowGenerationManager
    from conflowgen import ModeOfTransport
    from conflowgen import PortCallManager
    from conflowgen import ExportFileFormat
    from conflowgen import ExportContainerFlowManager
    from conflowgen import DatabaseChooser
    from conflowgen import setup_logger
    from conflowgen import InboundAndOutboundVehicleCapacityPreviewReport
    from conflowgen import ContainerFlowByVehicleTypePreviewReport
    from conflowgen import VehicleCapacityExceededPreviewReport
    from conflowgen import ModalSplitPreviewReport
    from conflowgen import InboundAndOutboundVehicleCapacityAnalysisReport
    from conflowgen import ContainerFlowByVehicleTypeAnalysisReport
    from conflowgen import ModalSplitAnalysisReport
    from conflowgen import ContainerFlowAdjustmentByVehicleTypeAnalysisReport
    from conflowgen import ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport


Database selection
==================

Now, we select a database to work in.
If the selected database already exists within the project folder, it is loaded.
Otherwise, it is created.

.. code-block:: python

    database_chooser = DatabaseChooser()
    demo_file_name = "my_demo.sqlite"
    if demo_file_name in database_chooser.list_all_sqlite_databases():
        database_chooser.load_existing_sqlite_database(demo_file_name)
    else:
        database_chooser.create_new_sqlite_database(demo_file_name)


General settings
================

We use the :meth:`ContainerFlowGenerationManager.set_properties` method of the
:class:`ContainerFlowGenerationManager` class to set a ``name``, the ``start_date`` and the ``end_date`` for the
generation process.
The ``start_date`` and ``end_date`` parameters must be provided as a datetime.date.
In our example, the ``end_time`` is set as a 21 day interval on top of the ``start_date`` which is set to the time of
execution.
Other general settings can be set here, see the :class:`ContainerFlowGenerationManager` class for more information.

.. code-block:: python

    container_flow_generation_manager = ContainerFlowGenerationManager()
    container_flow_generation_manager.set_properties(
        name="Demo file",
        start_date=datetime.datetime.now().date(),
        end_date=datetime.datetime.now().date() + datetime.timedelta(days=21)
    )


Creating schedules
==================

In this demo script we will exemplary add and specify one feeder liner service to the generator.
We do this by using the :meth:`.PortCallManager.add_large_scheduled_vehicle` method.
The concrete vehicle instances are only generated when :meth:`.ContainerFlowGenerationManager.generate` is invoked.

.. code-block:: python

    port_call_manager = PortCallManager()

At first we define a name for our new feeder liner service.

.. code-block:: python

    feeder_service_name = "LX050"

By using the :meth:`.add_large_scheduled_vehicle` method, we can define the attributes for our feeder service.

* ``vehicle_type`` defines, that we deal with a feeder as the mode of transport. Other valid modes of transport are deep_sea_vessel, barge, or train.
* ``service_name`` defines a fictional name for that service.
* ``vehicle_arrives_at`` specifies the date where the first port call of this particular line is usually happening. This parameter must be a datetime.date.
* ``vehicle_arrives_at_time`` sets the average / planned / scheduled timeslot of the port call. This parameter must be a datetime.time.
* ``average_vehicle_capacity`` defines the average capacity of the vessels utilized on this line. Parameter must be int or float.
* ``average_moved_capacity`` sets the capacity which is in average moved between the feeder and the terminal at each call. Parameter must be int or float.
* ``next_destinations`` can be set, consisting of name and frequency which can e.g. be used as implication for storage- and stacking-problems. A list of tuples [str, float] is expected here.

.. code-block::

    port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.feeder,
            service_name=feeder_service_name,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=[
                ("DEBRV", 0.4),  # 40% of the containers go here...
                ("RULED", 0.6)   # and the other 60% of the containers go here.
            ]
        )

The overall code in the demo for the creation of a feeder service looks like this.
Here, the code is wrapped in an if condition to check if the liner service is not already existing and comes with some
additional logging information.
The logging part may be helpful, but is not explained further here.

.. code-block:: python

    port_call_manager = PortCallManager()
    feeder_service_name = "LX050"
    if not port_call_manager.get_schedule(feeder_service_name, vehicle_type=ModeOfTransport.feeder):
        logger.info(f"Add feeder service '{feeder_service_name}' to database")
        port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.feeder,
            service_name=feeder_service_name,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=[
                ("DEBRV", 0.4),  # 40% of the containers go here...
                ("RULED", 0.6)   # and the other 60% of the containers go here.
            ]
        )
    else:
        logger.info(f"Feeder service '{feeder_service_name}' already exists")

Following the same principle and structure we can also add schedules for trains and deep sea vessels:

.. code-block:: python

    train_service_name = "JR03A"
    if not port_call_manager.get_schedule(train_service_name, vehicle_type=ModeOfTransport.train):
        logger.info(f"Add train service '{train_service_name}' to database")
        port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.train,
            service_name=train_service_name,
            vehicle_arrives_at=datetime.date(2021, 7, 12),
            vehicle_arrives_at_time=datetime.time(17),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
            next_destinations=None  # Here we don't have containers that need to be grouped by destination
        )
    else:
        logger.info(f"Train service '{train_service_name}' already exists")

.. code-block:: python

    deep_sea_service_name = "LX050"
    if not port_call_manager.get_schedule(deep_sea_service_name, vehicle_type=ModeOfTransport.deep_sea_vessel):
        logger.info(f"Add deep sea vessel service '{deep_sea_service_name}' to database")
        port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name=deep_sea_service_name,
            vehicle_arrives_at=datetime.date(2021, 7, 10),
            vehicle_arrives_at_time=datetime.time(19),
            average_vehicle_capacity=16000,
            average_moved_capacity=150,  # for faster demo
            next_destinations=[
                ("ZADUR", 0.3),  # 30% of the containers go to ZADUR...
                ("CNSHG", 0.7)   # and the other 70% of the containers go to CNSHG.
            ]
        )
    else:
        logger.info(f"Deep sea service '{deep_sea_service_name}' already exists")

Generate the data
=================

After we have set some exemplary schedules, we can now come to the actual generation.
The :meth:`ContainerFlowGenerationManager.generate` method starts the generation process of the synthetic
container flow data, based on the information you set earlier.

.. code-block:: python

    container_flow_generation_manager.generate()

