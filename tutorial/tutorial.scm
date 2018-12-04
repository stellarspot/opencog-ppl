(use-modules (opencog) (opencog query) (opencog exec))

; Probability Distributions

; Bernoulli distribution
(EvaluationLink
 (Predicate "probability-distribution-bernoulli")
 (Number "0.5")) ; success probability (real [0, 1])

; Binomial distribution
(EvaluationLink
 (Predicate "probability-distribution-binomial")
 (ListLink
  (Number "0.5") ; success probability (real [0, 1])
  (Number "4"))) ; number of trials (int (>=1))


; A has bernoulli distribution
(EvaluationLink
 (Predicate "probability")
 (ListLink
  (Concept "A")
  (EvaluationLink
   (Predicate "probability-distribution-bernoulli")
   (Number "0.5"))))


; Probability Expressions

; P(not A and B)
(Predicate "probability-and"
 (ListLink
  (EvaluationLink
   (Predicate "probability-not")
   (Concept "A"))
  (Concept "B")))


; P(A and B | A or B)
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
    (Concept "B")))))