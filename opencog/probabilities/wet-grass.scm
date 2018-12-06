(use-modules (opencog) (opencog query) (opencog exec))

; Bayesian Network

; Value Types

; True/False values
(InheritanceLink (Concept "False") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "True") (Concept "TrueFalseValue"))

; Device values
(InheritanceLink (Concept "Off") (Concept "switch"))
(InheritanceLink (Concept "On") (Concept "switch"))

; Probabilities

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "True")))

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "False")))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "False"))
  (AssociativeLink (Concept "Sprinkler") (Concept "False"))
 )
)

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "False"))
  (AssociativeLink (Concept "Sprinkler") (Concept "True"))
 )
)
