# Belief Propagation Samples

## Holmes Grass, Watson Grass, Sprinkler and Rain

Example: Sherlock Holmes and wet grass

HG - grass is wet on Holmes's lawn  
WG - grass is wet on Watson's lawn  
S - sprinkler was turned on  
R - there was a rain

![Bayesian Network](images/belief_propagation/holmes_grass_bayesian_network.png)

P(HG, WG, S, R) = P(HG|S,R) P(WG|R)  P(S) * P(R)

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


Was there a rain if Holmes's grass is wet?

P(R=true|HG=wet) = P(R=true, HG=wet) / P(HG=wet)
  = Sum[S, WG] P(HG=wet, WG, S, R=true) / Sum[WG, S, R] P(HG=wet, WG, S, R)


P(R=true, HG=wet)   
= Sum[S, WG] P(R=true, HG=wet, S, WG)  
= Sum[S, WG] (P(HG=wet|S,R=True) P(WG|R=True) P(S) P(R=True))  
= P(R=True) (Sum[WG]  P(WG|R=True) (Sum[S] P(HG=wet|S,R=True) P(S))  
=  0.2 * ( 1 ) * (1 + 1) = 0.4


P(HG=wet)   
= Sum[WG, S, R] P(HG=wet, WG, S, R)  
= Sum[WG, S, R] (P(HG=wet|S,R) P(WG|R) P(S) P(R))    
= Sum[R] P(R) (Sum[WG] P(WG|R)) (Sum[S] P(HG=wet|S,R) P(S))  
= 0.2 (1 + 0) (1 * 0.1 + 1 * 0.9) + 0.8 (0.2 + 0.8) (0.9 * 0.1 + 0 * 0.9)  
= 0.2 + 0.072 = 0.272

Was there a rain if Holmes's and Watson's grass is wet?

P(R=true|HG=wet, WG=wet) = P(R=true, HG=wet, WG=wet) / P(HG=wet, WG=wet)
  = Sum[S] P(HG=wet, WG=wet, S, R=true) / Sum[S, R] P(HG=wet, WG=wet, S, R)



## Traffic Light and Risk given Risk

Traffic Light: Green, Yellow, Red  
Risk: high, low

P(TL)

|Green|Yellow|Red |
|-----|------|----|
|  0.4|  0.25|0.35|

P(R|TL)

|      |  high|       low|
|------|------|----------|
|Green |0.1   |      0.9 |
|Yellow|0.55  |      0.45|
|Red   |0.95  |      0.05|

P(R, TL) = P(R|TL) P(TL)

Evidence:
R=High

Goal: P(TL=Yellow|R=High)

P(TL=Yellow|R=High) = P(R=High, TL=Yellow) / P(R=High) = P(R=High, TL=Yellow) / Sum[TL] P(R=High, TL) =  
P(R=High | TL=Yellow) P(TL=Yellow)/ Sum[TL] (P(R=High | TL) P(TL))

P(TL=Yellow|R=High) =  0.55 * 0.25 / (0.1 * 0.4 + 0.55 * 0.25 + 0.95 * 0.35) = 0.1375 / 0.51 = 0.27

### Message Passing

tensor = [[0.1, 0.9], [0.55, 0.45], [0.95, 0.05]]

tensor given risk high:  [[0.1], [0.55], [0.95]]

Bayesian Network: TL <-- Risk

Factor Graph:
P(R, TL) = P(R|TL) P(TL) = P1(R, TL) P2(TL)

P1    P2  
^     ^  
|  \  |  
R     TL  


R - P1 - TL - P2


## Rain and Wet Grass

Rain: true, false  
WatsonGrass: wet, dry

P(R)

|true |false |
|-----|------|
|  0.2|   0.8|

P(WG|R)

|    R|   wet|       dry|
|-----|------|----------|
|true |0.9   |      0.1 |
|false|0.25  |      0.75|


P(WG, R) = P(WG|R) P(R)

![Watson Grass and Rain](images/belief_propagation/watson_grass_and_rain_factor_tree.png)

### Message Pasing

Tensors:
* Tensor[P4]= [0.2, 0.8]
* Tensor[P2]= [[0.9, 0.1], [0.25, 0.75]]


Initial Messages:
* Message[WG->P2]=[1, 1]
* Message[P4->R]=[0.2, 0.8]

Step 1:
* Message[R->P2]=[0.2, 0.8]
* Message[P2->R]=[[0.9, 0.1], [0.25, 0.75]] * [1, 1 (index WG = 1)] = [1, 1]

Step 2:
* Message[P2->WG]=[[0.9, 0.1], [0.25, 0.75]] * [0.2, 0.8 (index R = 0)]  = [0.38 0.62]
* Message[R->P4]=[1, 1]


### Probability of Rain given Wet Grass

The task is to calculate a probability of rain given grass is wet:

P(R=true|WG=wet) = P(R=true, WG=wet) / P(WG=wet)


## Traffic Light and Risk

Traffic Light: Green, Yellow, Red  
Risk: high, low

P(TL)

|Green|Yellow|Red |
|-----|------|----|
|  0.4|  0.25|0.35|

P(R|TL)

|      |  high|       low|
|------|------|----------|
|Green |0.1   |      0.9 |
|Yellow|0.55  |      0.45|
|Red   |0.95  |      0.05|

P(R, TL) = P(R|TL) P(TL)

### Message Passing

tensor = [[0.1, 0.9], [0.55, 0.45], [0.95, 0.05]]
