Background
----------

In maritime logistics, simulation and optimization are commonly used methods for planning, solving problems and
evaluating solutions.
For testing new solutions, an extensive amount of realistic data are urgently needed but constantly scarce.
Since comprehensive real-life data are often unavailable or are classified, the generation of synthetic data is a
helpful way to get around this issue.
Sometimes even the owners of comprehensive container flow data can benefit from synthetic data,
e.g. for testing their business models, as well as to improve and adapt to the future.
A synthetic data generator for the creation of incoming and outgoing containers from the perspective of a maritime
container terminal has already been proposed by
:cite:t:`hartmann2004generating`.
Since his approach is now more than 15 years old, there are significant changes in the shipping industry.
We took this changes as a motivation to rethink, rework, and improve the existing generator.
Therefore, we created an improved container flow generator, named ConFlowGen, which allows the user to create synthetic
but yet realistic data of container flows for maritime container terminals.


Separated scenario generation
=============================

When setting up experiments, e.g. for discrete-event simulation or mathematical optimization, sometimes it might be
tempting to randomly generate vehicles and containers including all their properties and relations on-the-fly when
needed.
By having everything at one place (e.g. inside one simulation model), sharing the model is made easier as dependencies
on external files are minimized.
However, it turns the model into a monolithic structure.
It might be difficult to re-use parts of it in later projects from a technical perspective as no clear separation of
concerns might exist.
The assumptions used in the data generation process might be intertwined with the code that generates the data, making
it also difficult to track (and adjust) the assumptions within an ongoing project.
Overall, the monolithic structure is difficult to extend in future projects, reducing the value of the model.
In addition, creating data on-the-fly makes debugging rather difficult as the only reliable way to examine the generated
data is to actually run the (probably time-consuming) experiment.

ConFlowGen follows a more modular approach which is depicted in
:numref:`separated-traffic-demand-scenario-process`.
The data generation process itself is provided, so that the user only needs to define the input data,
i.e. schedules and distributions regarding the vehicle and container properties.
Thus, it is easier for the user to only document the assumptions without the need to discuss the details of the
underlying algorithm that assigns the container to its two vehicles
(one vehicle delivers the container on its inbound journey to the terminal and
one vehicle picks up the container from the terminal on its outbound journey).
Once a new model is capable of reading in ConFlowGen data, different container flow scenarios can easily be tested by
just exchanging the Excel files or CSV files.
The data generation process has been thoroughly checked with a range of unit tests so that several types of mistakes can
be excluded right from the start, thus making the debugging process easier.
In addition, ConFlowGen comes with several automated analyses regarding the expected KPIs of the maritime container
terminal.
These are designed to support the user to check whether the generated data is plausible for their specific case.
A final check for the plausibility of the generated data with an external tool is strongly suggested.


.. figure:: images/separate_traffic_demand_scenarios_from_simulation.svg
   :name: separated-traffic-demand-scenario-process
   :width: 80%

   Separating the container flow generation from running the experiments


Concept of data generation
==========================

The software is a conceptional elaboration of :cite:t:`hartmann2004generating`.
In :numref:`generation-process`, the process diagram of the software is shown.
First, an SQLite database is picked for persisting the user input and the generated container flow data.
The SQLite database file can be easily shared between users.
Second, the input data is added and the default values are modified according to one's needs.
In the third step, the data is generated.
This is further elaborated in the lower part of the process diagram colored in green.
In the last step, the data is exported to a tabular format, e.g. XLSX or CSV.

.. figure:: images/generation_process.svg
   :name: generation-process
   :width: 100%

   The generation process in ConFlowGen.

Input Data
~~~~~~~~~~

The required input data can be grouped as such:

- Services: vessels and trains belong to certain services that determine the schedule.
- Container property distributions: length, weight, and type (standard, reefer, IMO, ...).
- The next destination is also included for export and transshipment containers.
  The destination helps identifying container groups if e.g. the synthetic data is later utilized to investigate container
  stacking processes (i.e., containers with the same destination might be kept in the same bay and in the same yard block).
- The vehicle-type-dependent modal split
  (i.e., how frequently a container is picked up by a vehicle of a specific vehicle type given the vehicle type the
  container is delivered by).

Data Generation Process
~~~~~~~~~~~~~~~~~~~~~~~

Once
:meth:`.ContainerFlowGenerationManager.generate`
is invoked,
the data generation process is triggered.
It consists of several steps that are also depicted in
:numref:`generation-process`.

#. Creation of vehicles for services:
   All schedules are checked.
   For each arrival at the terminal within the start date and end date, one vehicle instance is created.
#. Creation of containers:
   Load the containers on the freshly-generated vehicles.
   These are the containers the vehicles deliver to the terminal on their inbound journey.
#. Assigning container to outbound journey:
   After a container has arrived at the terminal, it somehow must leave it again.
   A vehicle is chosen that obeys all operational constraints.
#. Creation of trucks for import containers:
   For all containers that are picked up by a truck, the corresponding truck is generated.
   Here, they are referred to as import containers.
   More precisely, these are just trucks that pick up containers - including domestic traffic as well.
#. Allocation of export containers:
   For all containers that are delivered by truck to the terminal, first the container is allocated on the vehicles
   generated in the first step.
   More precisely, these are just containers that are delivered by a truck but continue their journey on some kind of
   vessel or train - including domestic traffic as well.
#. Generate trucks that deliver the export containers.
   For the containers that were allocated in the previous step, now the trucks are generated.
#. Last, the destination of the container is determined.
   This step is only executed for those containers that are loaded on a vessel or train for which the next destinations
   (ports or intermodal terminals) have been provided.

Output Data
~~~~~~~~~~~

The output of this tool is in a tabular format.
One table exists for each of the vehicle kinds and one table contains the information for each container.
Each row in the respective vehicle table represents a single vehicle including its static and journey-specific features.
Further, for each container two vehicle IDs are provided -
one for the vehicle that delivers the container and one for the vehicle that picks it up.
As a result, the container's journey-specific attributes are collected from these two vehicles.
