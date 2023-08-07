Background
----------

In maritime logistics, simulation and optimization are commonly used methods for planning, solving problems and
evaluating solutions.
For testing new solutions, an extensive amount of realistic data are urgently needed but constantly scarce.
Since comprehensive real-life data are often unavailable or are classified, the generation of synthetic data is a
helpful way to get around this issue.
One such instance is when we want to study of the dynamics at a container terminal.
They are nodes which connect the seaside with the hinterland, transshipping containers between vessels of different
sizes, trains, and trucks (see
:numref:`container-terminal`
for reference).
The container terminal functions as a buffer between these and offers to keep the containers in the yard for some hours
or days.
The data describing the arrival of each of these vehicle at the container terminal including the containers it unloads
and loads are called container flow data in the following.

When examining new approaches quantitatively (e.g. by means of simulation or optimization experiments), it is helpful
to generate scenarios that approximate the day-to-day operations at a container terminal without losing generality.
This is true both in academia and industry.
Sometimes even the owners of comprehensive container flow data can benefit from synthetic data,
e.g. when testing new processes or estimating the impact of current developments.
In both cases, no operational data of these cases can exist and the generation must be (partly) driven by assumptions.

A synthetic data generator capable of generating container flow data has been previously proposed by
:cite:t:`hartmann2004generating`.
Since his approach is now more than 15 years old, there are significant changes in the shipping industry.
We took this changes as a motivation to rethink, rework, and improve the existing generator conceptually.
Therefore, we created an improved container flow generator, named ConFlowGen, which allows the user to create synthetic
but yet realistic data of container flows for maritime container terminals.
It has been first academically described in
:cite:t:`kastner2022conflowgen`,
including a discussion of recent developments in the shipping industry as well as related academic synthetic data
generators.


.. figure:: images/container_terminal.svg
   :name: container-terminal
   :align: center
   :width: 80%

   A container terminal serves different interfaces

Separated Scenario Generation
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
   :align: center
   :width: 80%

   Separating the container flow generation from running the experiments


Concept of Data Generation
==========================

The software is a conceptional elaboration of :cite:t:`hartmann2004generating`.
In :numref:`generation-process`, the process diagram of the software is shown.
First, an SQLite database is picked for persisting the user input and the generated container flow data.
The SQLite database file can be easily shared between users.
Second, the input data is added and the default values are replaced with the specific assumptions of the user.
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
  (i.e., given the vehicle type with which the container is delivered to the container terminal, which vehicle type is
  used for the outbound journey of the container?).

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

There is no concept of handling times, neither at the interfaces nor in the yard.
Determining these will be the task of the simulation or optimization model using this data.

Output Data
~~~~~~~~~~~

The output of this tool is in a tabular format.
One table exists for each of the vehicle kinds and one table contains the information for each container.
Each row in the respective vehicle table represents a single vehicle including its static and journey-specific features.
Further, for each container two vehicle IDs are provided -
one for the vehicle that delivers the container and one for the vehicle that picks it up.
As a result, the container's journey-specific attributes are collected from these two vehicles.

Academic Discussion
===================

ConFlowGen has been created in the context of academic research while having a clear application in mind.

Similar projects
~~~~~~~~~~~~~~~~

With ConFlowGen, we have extended a certain tradition in academia to synthetically generate use cases for operational
research in maritime logistics.
As previously elaborated, we have built upon concepts first introduced by :cite:t:`hartmann2004generating`.
While assessing the currently available alternatives, among others we have come across the following existing solutions:

- In order to reduce the number of unproductive container moves,
  :cite:t:`exposito2012marshalling`
  developed a heuristic solution method.
  To test the solution method under various conditions, they also developed an instance generator that is located at
  :cite:`exposito2012marshalling-software`.

- :cite:t:`briskorn2019generator`
  developed a test data generator that may be used to simulate yard crane container handling processes.
  Their generic approach generates test examples of crane scheduling issues.

- A technique for the evaluation of quay crane scheduling models and solution methods is presented by
  :cite:t:`meisel2011unified`.
  They developed an instance benchmark generator, with the goal of creating test scenarios for exhibiting the potentials
  and comparing models that handle the quay crane scheduling problem.
  The generator can be found at
  :cite:`meisel2011unified-software`.

Most likely, this list is not exhaustive and there is more software available online to synthetically generate data for
evaluating new solutions in the field of maritime logistics.
If you know about a suitable candidate or you have even developed one yourself, please feel free to reach out to
marvin.kastner@tuhh.de.
We are more than pleased to discuss the topic and add it to the list if suitable.

Presentation of ConFlowGen
~~~~~~~~~~~~~~~~~~~~~~~~~~

ConFlowGen has been first presented at the International Conference on Dynamics in Logistics in February 2022.
If ConFlowGen served you well in your research, and you would like to acknowledge the project in your publication,
we would be glad if you mention our work as defined in our
`CITATION.cff <https://raw.githubusercontent.com/1kastner/conflowgen/main/CITATION.cff>`_.
If you just need a BibTeX entry for your citation software, this one should do the job:

.. code-block:: bibtex

   @inproceedings{Kastner_Container_Flow_Generation_2022,
      address = {Bremen, DE},
      author = {Kastner, Marvin and Grasse, Ole and Jahn, Carlos},
      editors = {Freitag, Michael and Kinra, Aseem, and Kotzab, Herbert, and Megow, Nicole},
      booktitle = {Dynamics in Logistics. Proceedings of the 8th International Conference {LDIC} 2022, {Bremen, Germany}},
      doi = {10.1007/978-3-031-05359-7_11},
      month = {2},
      pages = {133--143},
      publisher = {Springer Cham},
      series = {Lecture Notes in Logistics},
      title = {Container Flow Generation for Maritime Container Terminals},
      year = {2022}
   }

At a second occasion, ConFlowGen has been presented at the Annual General Assembly of the
World Association for Waterborne Transport Infrastructure (PIANC)
in 2023 in Oslo.
The contribution
`Synthetically generating traffic scenarios for simulation-based container terminal planning \
<https://tore.tuhh.de/dspace-cris-server/api/core/bitstreams/1d990927-cca9-4b40-8440-19cc544cc847/content>`_
has been awarded with the
`De Paepe-Willems Award <https://www.pianc.org/award/de-paepe-willems-award/>`_.
The paper highlights how ConFlowGen can support terminal planners in designing terminal interfaces and determining
the required yard capacity.
