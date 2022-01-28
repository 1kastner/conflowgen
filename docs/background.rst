Background
----------

In maritime logistics, simulation and optimization are commonly used methods for planning, solving problems and
evaluating solutions.
For testing new solutions, an extensive amount of realistic data are urgently needed but constantly scarce.
Since comprehensive real-life data are often unavailable or are classified, the generation of synthetic data is a
helpful way to get around this issue.
Sometimes even the owners of comprehensive container flow data can benefit from
synthetic data, e. g. for testing their business models, as well as to improve and adapt to the future.
A synthetic data generator for the creation of incoming and outgoing containers from the perspective of a maritime
container terminal has already been proposed by :cite:t:`hartmann2004generating`.
Since his approach is now more than 15 years old, there are significant changes in the shipping industry.
We took this changes as a motivation to rethink, rework, and improve the existing generator.
Therefore, we created an improved container flow generator, named ConFlowGen, which allows the user to create synthetic
but yet realistic data of container flows for maritime container terminals.


Concept of Data Generation
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
