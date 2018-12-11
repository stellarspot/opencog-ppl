(use-modules (opencog) (opencog query) (opencog exec))

; Bayesian Network
; Belief Propagation

; Types
(InheritanceLink (Concept "true") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "false") (Concept "TrueFalseValue"))

(InheritanceLink (Concept "switch-on") (Concept "Switch"))
(InheritanceLink (Concept "swithc-off") (Concept "Switch"))

(InheritanceLink (Concept "is-wet") (Concept "Wet"))
(InheritanceLink (Concept "is-not-wet") (Concept "Wet"))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "Rain") (Concept "TrueFalseValue")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "Sprinkler") (Concept "Switch")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "WatsonGrass") (Concept "Wet")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "HolmesGrass") (Concept "Wet")))

; Sherlock Holmes and wet grass

; Rain
; P(R)
; true 0.2
; false 0.8

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "true" (stv 0.2 1))))


(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "false" (stv 0.8 1))))


; Sprinkler
; P(S)
; switch-on  0.1
; swithc-off 0.9

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" (stv 0.1 1))))

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" (stv 0.9 1))))


; P(HG=T|WG=T)


; Watson grass is wet
; P(WG = T)
; true 1

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "WatsonGrass") (Concept "true" (stv 1.0 1))))


; Holmes grass is wet
; P(HG = T)
; true 1

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "HolmesGrass") (Concept "true" (stv 1.0 1))))