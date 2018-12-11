(use-modules (opencog) (opencog query) (opencog exec))

; Bayesian Network
; Belief Propagation

; Types
(InheritanceLink (Concept "true") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "false") (Concept "TrueFalseValue"))

(InheritanceLink (Concept "switch-on") (Concept "Switch"))
(InheritanceLink (Concept "swithc-off") (Concept "Switch"))

(InheritanceLink (Concept "wet") (Concept "Grass"))
(InheritanceLink (Concept "dry") (Concept "Grass"))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "Rain") (Concept "TrueFalseValue")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "Sprinkler") (Concept "Switch")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "WatsonGrass") (Concept "Grass")))

(EvaluationLink
 (PredicateNode "type")
 (AssociativeLink (Concept "HolmesGrass") (Concept "Grass")))

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
; switch-off 0.9

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" (stv 0.1 1))))

(EvaluationLink
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" (stv 0.9 1))))

; Watson grass
; P(WG|R)
; R      wet  dry
; true   1.0  0.0
; false  0.2  0.8

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 0.2 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.8 1)))))

; Holmes grass
; P(HG|R)
; S          R      wet  dry
; switch-on  true   1.0  0.0
; switch-on  false  0.9  0.1
; switch-off true   1      0
; switch-off false  0      1

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 0.9 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.1 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 0.0 1)))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 1.0 1)))))

; P(HG=T|WG=T)

; Evidence: Watson grass is wet
; P(WG = T)
(EvaluationLink
 (PredicateNode "evidence")
 (AssociativeLink (Concept "WatsonGrass") (Concept "wet" (stv 1.0 1))))

; Evidence Holmes grass is wet
; P(HG = T)
(EvaluationLink
 (PredicateNode "evidence")
 (AssociativeLink (Concept "HolmesGrass") (Concept "wet" (stv 1.0 1))))