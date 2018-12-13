# Conditional Probability Inference in PLN

## Rain and Grass task

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