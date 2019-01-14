# experiments
Small personal projects and experiments

## ACO - An Ant Colony Optimization simulation
A simple ant colony optimization simulation. There are three main parts, the landscape which plays the role of environment, the ant colony which optimizes its behavior for the landscape and the visualization.

### Landscape
The landscape is created by generating random points. These are then used by a delaunay triangulation algorithm to generate a graph representing the landscape.
The landscape the spawns ant colonies and food for the ants to gather. Each time a pile of food is emptied new food is created on another random node.

### Colony
The ant colony tries to gather as much food as possible.
It optimizes in discrete iterations in which an ant population is created.
Each iteration a population is spawned that walks over the landscape graph. Successful ants spread pheromones over the path the have walked depending on the length of the path.
Subsequent ants are more likely to take paths that have more pheromones on them. Finally this converges to an optimal path to the food.

Finally the pheromones have a rate of decay, so paths that are not used are forgotten and when a pile of food is finished ants will start exploring for more food.

### Visualization
The visualization is done with pygame and shows the graph of the landscape with the locations of the colony and food.
On the edges of the graph the density of pheromones is shown.

## BDD2AIG - A BDD to AIG Format converter

A program for transforming BDD's (Binary Decision Diagrams) into AIG's (And-Inverter Graphs).

`spinx` can be used to generate docs.

### BDD
A binary decision diagram is a generalization of decision trees, that can lead to an exponentially smaller representation in many cases.
BDD's can be used for several applications. It is often used to reperesent a boolean formula, in this case it represents a truth table. Each satisfying assignment has a corresponding path to the true node. The representation allows for the efficient application of several operations such as uniformly sampling satisfying assignments and enumerating or counting assignments.

Another use of BDD is to allow for very compact representation of sets and relations (or functions). This is often used in model checking to allow for efficient symbolic operations and to minimize the memory needed.

### AIG
An and-inverter graph is a simplified representation of a circuit, each gate can be represented as a combination of `and` and `or` gates. The advantage of such a graph is that it allows for optimizations and algorithms that are otherwise difficult and it can be stored in an efficient format (AIGER).

### Conversion
The conversion consists of several steps:

1) Transform the BDD into a normal circuit.
2) Replace all non-and/not gates with their representation in and and not gates.
3) Label all gates/connectors/inputs and transform them in to the AIGER file format. 