## Data Declaration

Atomese allows to define [TruthValue](https://wiki.opencog.org/w/TruthValue) (strength and confidence)
for an atom:
`(Concept "A" (stv 0.8 0.3))`

However, WebPPL provides different kinds of
[probability distributions](https://webppl.readthedocs.io/en/master/distributions.html)
which are also useful to implement in OpenCog.

Bernoulli distribution:

WebPPL `var distribution = Bernoulli({p: 0.5});`

OpenCog:
```scheme
(EvaluationLink
 (Predicate "probability-distribution-bernoulli")
 (Number "0.5")) ; success probability (real [0, 1])
```

Binomial distribution:

WebPPL `var distribution = Binomial({p: 0.5, n: 4});`

OpenCog:
```scheme
(EvaluationLink
 (Predicate "probability-distribution-binomial")
 (ListLink
  (Number "0.5") ; success probability (real [0, 1])
  (Number "4"))) ; number of trials (int (>=1))
```

"A" concept with Bernoulli probability distribution:
```scheme
(EvaluationLink
 (Predicate "probability")
 (ListLink
  (Concept "A")
  (EvaluationLink
   (Predicate "probability-distribution-bernoulli")
   (Number "0.5"))))
```

## Probability expressions

Probability Expression: P(not A and B)

WebPPL `!A & B`

OpenCog
```scheme

(Predicate "probability-and"
 (ListLink
  (EvaluationLink
   (Predicate "probability-not")
   (Concept "A"))
  (Concept "B")))
```

## Conditional Probability

Probability ( A and B | A or B )
WebPPL:
```
var generateCondProb = function () {
    var x = flip(0.5)
    var y = flip(0.5)
    condition(x || y)
    return x & y
}

Infer({method: 'enumerate', model: generateCondProb})
```

OpenCog
```scheme
(EvaluationLink
 (Predicate "probability-conditional")
 (ListLink
  ; condition expression
  (Predicate "probability-or"
   (ListLink
    (Concept "A")
    (Concept "B")))
  ; main expression
  (Predicate "probability-and"
   (ListLink
    (Concept "A")
    (Concept "B")))))```
```

## Samples

OpenCog:
* [OpenCog Alarm](opencog/probabilities/alarm.scm)
* [OpenCog Balls in Basket](opencog/probabilities/alarm.scm)

WebPPL
* [WebPPL Alarm](webppl/probabilities/alarm.js)
* [WebPPL Condition P(x and y | x or y)](webppl/probabilities/probabilities.js)
