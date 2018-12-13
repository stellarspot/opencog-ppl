# Conditional Probability Inference in PLN

## Rain and Grass task

Lets take a simple task where there is a rain and grass with conditional probabilities:

Rain:

| T   | F   |
| --- | --- |
| 0.2 | 0.8 |

Grass:

| Rain\Grass | T   | F   |
| ---------- | --- | --- |
| T          | 0.8 | 0.2 |
| F          | 0.1 | 0.9 |

To find if grass is wet it needs to calculate a marginal distribution:

P(Grass=true)=P(Grass=true, Rain=true) + P(Grass=true, Rain=false)
  = P(Grass=true | Rain=true) P(Rain=true) + P(Grass=true | Rain=false) P(Rain=false)

P(Grass=true) = 0.8 * 0.2 + 0.1 * 0.8 = 0.24

The same task can be solved by PLN.
It is under question should the joint probability be used instead of conditional for PLN.

```scheme
(use-modules (opencog) )

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; PLN with Probabilities

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))


; Grass
(ImplicationLink (stv 0.8 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "true")))

(ImplicationLink (stv 0.2 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "false")))

(ImplicationLink (stv 0.1 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "true")))

(ImplicationLink (stv 0.9 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "false")))

(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "true"))
 ))
```

The result is:
```scheme
(SetLink
   (AssociativeLink (stv 0.12 1)
      (ConceptNode "Grass")
      (ConceptNode "true")
   )
)
```
Which infers the probability 0.12 that the grass is wet which is twice lower than for manual calculation.