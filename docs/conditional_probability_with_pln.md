# Conditional Probability Inference in PLN

## Rain and Grass

Lets take a simple task where there is a rain and grass with conditional probabilities:

Rain:

| true | false |
| ---- | ----- |
| 0.2  | 0.8   |

Grass:

| Rain\Grass | wet | dry |
| ---------- | --- | --- |
| true       | 0.8 | 0.2 |
| false      | 0.1 | 0.9 |

To find if grass is wet it needs to calculate a marginal distribution:

P(Grass=wet)=P(Grass=wet, Rain=true) + P(Grass=wet, Rain=false)
  = P(Grass=wet | Rain=true) P(Rain=true) + P(Grass=wet | Rain=false) P(Rain=false)

P(Grass=wet) = 0.8 * 0.2 + 0.1 * 0.8 = 0.24

The same task can be solved by PLN.
It is under question should the joint probability be used instead of conditional for PLN.

```scheme
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; PLN with Probabilities

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))

; Grass
(ImplicationLink (stv 0.8 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.2 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.1 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.9 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "dry")))

(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "wet"))
 ))
```

The result is:
```scheme
(SetLink
   (AssociativeLink (stv 0.32 1)
      (ConceptNode "Grass")
      (ConceptNode "wet")
   )
)
```
Which infers the probability 0.12 that the grass is wet which is twice lower than for manual calculation.

## Rain, Sprinkler and Grass

Lets look at task where there also is a sprinkler which can have states on and off.
We assume that sprinkler state is independent from the rain.

Rain:

| true | false |
| ---- | ----- |
| 0.2  | 0.8   |

Sprinkler:

| true | false |
| ---- | ----- |
| 0.4  | 0.6   |

Grass:

| Rain  | Sprinkler | wet | dry |
| ----- | --------- | --- | --- |
| true  | on        | 0.9 | 0.1 |
| true  | off       | 0.8 | 0.2 |
| false | on        | 0.6 | 0.3 |
| false | off       | 0.1 | 0.9 |


P(Grass=wet) =
    P(Grass=wet, Rain=true,  Sprinkler=on) + P(Grass=wet, Rain=true,  Sprinkler=off) +
    P(Grass=wet, Rain=false, Sprinkler=on) + P(Grass=wet, Rain=false, Sprinkler=off) =  
    P(Grass=wet | Rain=true, Sprinkler=on)   P(Rain=true) P(Sprinkler=on)   +
    P(Grass=wet | Rain=true, Sprinkler=off)  P(Rain=true) P(Sprinkler=off)  +
    P(Grass=wet | Rain=false, Sprinkler=on)  P(Rain=false) P(Sprinkler=on)  +
    P(Grass=wet | Rain=false, Sprinkler=off) P(Rain=false) P(Sprinkler=off)


In PLN the task looks like:
```scheme
(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))

; Sprinkler
(Associative (stv 0.4 1) (Concept "Sprinkler") (Concept "on"))
(Associative (stv 0.6 1) (Concept "Sprinkler") (Concept "off"))

; Grass
(ImplicationLink (stv 0.9 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.1 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.8 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.2 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.6 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.3 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.1 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.9 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "dry")))


; Call PLN
(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "wet"))
 ))
```

The result is:
```scheme
(SetLink
   (AssociativeLink
      (ConceptNode "Grass")
      (ConceptNode "wet")
   )
)
```

The result truth value has zero confidence: (stv 1 0)
