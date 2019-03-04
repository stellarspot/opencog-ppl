# Belief Propagation algorithm implementation in OpenCog


## Reference Implementation

[Belief Propagation in Python](../opencog/bayesian-network/factor-graph/belief_propagation.py)

[Algorithm and tests folder](../opencog/bayesian-network/factor-graph)

## Bayesian network

Example: Sherlock Holmes and wet grass

HG - grass is wet on Holmes's lawn  
WG - grass is wet on Watson's lawn  
S - sprinkler was turned on  
R - there was a rain

![Bayesian Network](images/belief_propagation/holmes_grass_bayesian_network.png)

P(HG, WG, S, R) = P(HG|S,R) P(WG|R) P(S) P(R)


### Conditional Probability Tables

Domain:  
Rain: true, false  
Sprinkler: switch-on, switch-off  
Grass: wet, dry

P(R)

|true |false |
|-----|------|
|  0.2|   0.8|

P(S)

|true |false |
|-----|------|
|  0.1|   0.9|

P(WG|R)

|    R|   wet|       dry|
|-----|------|----------|
|true |1     |         0|
|false|0.2   |       0.8|

P(HG|S, R)

|         S|    R|   wet|       dry|
|----------|-----|------|----------|
|switch-on |true |1     |         0|
|switch-on |false|0.9   |       0.1|
|switch-off|true |1     |         0|
|switch-off|false|0     |         1|

### Bayesian Network representation in OpenCog

Variables in Bayesian Network are represented as ConceptNode in OpenCog:
```python
rain = ConceptNode('Rain')
holmes_grass = ConceptNode('HolmesGrass')
```

Conditional dependencies are represented as ImplicationLink:
```python
# Watson Grass given Rain
ImplicationLink(rain, watson_grass)

# Holmes Grass given Sprinkler and Rain
ImplicationLink(ListLink(sprinkler, rain), holmes_grass)
```

Conditional probability tables are represented as NumPy tensors:
```python
# Rain a priory probability
rain.set_value(key_probability(), PtrValue(np.array([0.2, 0.8])))

# Watson Grass given Rain conditional probability table
watson_grass_given_rain_probability = np.array(
    [[1.0, 0.0],
     [0.2, 0.8]])

watson_grass_given_rain.set_value(key_probability(), PtrValue(watson_grass_given_rain_probability))
```

Wet Grass sample:
```python
# Define Variables
rain = ConceptNode('Rain')
sprinkler = ConceptNode('Sprinkler')
holmes_grass = ConceptNode('HolmesGrass')
watson_grass = ConceptNode('WatsonGrass')

# Define Conditional Dependencies
watson_grass_given_rain = ImplicationLink(rain, watson_grass)
holmes_grass_given_sprinkler_rain = ImplicationLink(ListLink(sprinkler, rain), holmes_grass)

# Define probabilities values
# Rain a priory probability
rain_probability = np.array([0.2, 0.8])
rain.set_value(key_probability(), PtrValue(rain_probability))

# Sprinkler a priory probability
sprinkler_probability = np.array([0.1, 0.9])
sprinkler.set_value(key_probability(), PtrValue(sprinkler_probability))

# Watson Grass given Rain conditional probability table
watson_grass_given_rain_probability = np.array(
    [[1.0, 0.0],
     [0.2, 0.8]])
watson_grass_given_rain.set_value(key_probability(), PtrValue(watson_grass_given_rain_probability))

# Holmes Grass given Sprinkler and Rain conditional probability table
holmes_grass_given_sprinkler_rain_probability = np.array(
    [[[1.0, 0.0],
      [0.9, 0.1]],
     [[1.0, 0.0],
      [0.0, 1.0]]])
holmes_grass_given_sprinkler_rain.set_value(key_probability(),
                                            PtrValue(holmes_grass_given_sprinkler_rain_probability))
```

# Conditional Probability calculation

Was there a rain if Holmes's grass is wet?

P(R=true|HG=wet) = P(R=true, HG=wet) / P(HG=wet)

P(R=true, HG=wet)  
= Sum[S, WG] P(HG=wet, WG, S, R=true)  
= Sum[S, WG] (P(HG=wet|S, R=true) P(WG|Rain=true) P(S) P(Rain=true))

P(HG=wet)  
= Sum[WG, S, R] P(HG=wet, WG, S, R)  
= Sum[WG, S, R] (P(HG=wet|S, R) P(WG|Rain) P(S) P(Rain))


The goal is to calculate marginalization of joint distribution P(R=true, HG=wet) and P(HG=wet).
This is what the Belief Propagation algorithm aimed for.

## Factorization

Create a bipartite graph where one set of vertices are functions and another set are variables:

P(HG, WG, S, R)  
= P(HG|S,R) P(WG|R) P(S) P(R)  
= P1(HG,S,R) P2(WG,R) P3(S) P3(R)

![Bayesian Network Factorization](images/belief_propagation/holmes_grass_factorization.png)

## Factor Tree

The algorithm will be used for trees:

![Bayesian Network Factor Tree](images/belief_propagation/holmes_grass_factor_tree.png)

## Messages sending on Factor tree

Message from variable i to factor f:  
M(i->f) = Mul[g, g!=f] M (g->i)

Initial message from variable i to factor f for leaf variables:  
M(i->f) = [1, 1, ... , 1]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_var_f.png)

Message from factor f to variable i:  
M(f->i) = Sum[j, j !=i] f(X) Mul(j, j!=i) M [j->f]

Initial message from factor f to variable i for leaf factors:  
M(i->f) = [f(V1), f(V2), ... , f(Vn)]

![Bayesian Network Factor Tree](images/belief_propagation/factor_tree_message_f_var.png)


## Run Belief Propagation algorithm

Belief Propagation algorithm allows to calculate marginal probabilities for the given evidence variables.


Create child AtomSpace before `belief_propagation(child_atomspace)` call and delete the child AtomSpace after it.

Set evidences:
* For each variable which has evidence it is necessary to set an evidence index

For example:
```python
# P(HolmesGrass=wet)
# HolmesGrass=wet, index=0
# HolmesGrass=dry, index=1
holmes_grass.set_value(key_evidence(), PtrValue(0))
```

Run the Belief Propagation algorithm to calculate marginalization:
```python
# P(HG=wet, R=true)
# P(HG=wet, WG, S, R=true)
# HG=wet, index=0
# R=true, index=0

child_atomspace = create_child_atomspace()
holmes_grass.set_value(key_evidence(), PtrValue(0))
rain.set_value(key_evidence(), PtrValue(0))
marginalization_dividend = belief_propagation(child_atomspace)

delete_child_atomspace()
```

## Belief Propagation algorithm

### Steps

Initialization:
* Create Factor Graph Variable for each ConceptNode('Name') with conditional probability table
  * Set name to 'Variable-Name'
  * If variable has evidence index
    * Set domain size to 1
    * Set conditional probability table to only one value
  * Otherwise
    * Set domain size
    * Set conditional probability table
* Create Factor Graph factor for each ImplicationLink(V1,.., Vn) with conditional probability table
  * Set name to 'Factor-V1-...-Vn'
  * Set Factor arguments as names of the provided variables
  * If a variable has evidence index
    * Reduce probability table to contain only values for the given evidence index
  * Otherwise
    * Set conditional probability table

Message Passing:

Message from variable i to factor f:
```text
If there is no messages from variable i to f:
  Get a set of edges from factor g to i where g!=f
    If the set is empty, send initial message M(i->f) = [1, ..., 1]
      where the vector size is the size of the variable i domain
    If the set size is number of incoming factors minus 1
        (all connected factors except f have messages to i)
      send componentwise multiplication of the messages
    Else do nothing (not all messages are received)
```

Message from factor f to variable i:
```text
If there is no messages from variable i to f:
  Get set of edges from variable j to factor f where j!=i
    If the set is empty, send initial message M(f->i)=[f(Xi=v1), ..., f(Xi)=vn]
      where the message size is the size of the variable i domain
    If the set size is number of incoming variables minus 1
        (all connected variables except i have messages to f)
      calculate tensor from F from f
        F = (f(X1=v11, X2=v21), ..., f(X1=v1n, X2=v2n))
      multiply the tensor F to all incoming messages except variable i:
      M(f->i)=Sum[k] F * M[k->f] where k!=i
    Else do nothing (not all messages are received)
```

Factor value calculation:
* for the given factor name find factor-argument-list
* for each variable get its domain