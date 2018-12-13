(use-modules (opencog) (opencog query) (opencog exec))

; Bayesian Network
; Belief Propagation

; Domains
(InheritanceLink (Concept "true") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "false") (Concept "TrueFalseValue"))

(InheritanceLink (Concept "switch-on") (Concept "Switch"))
(InheritanceLink (Concept "swithc-off") (Concept "Switch"))

(InheritanceLink (Concept "wet") (Concept "Grass"))
(InheritanceLink (Concept "dry") (Concept "Grass"))

(InheritanceLink (Concept "Rain") (Concept "TrueFalseValue"))
(InheritanceLink (Concept "Sprinkler") (Concept "Switch"))
(InheritanceLink (Concept "WatsonGrass") (Concept "Grass"))
(InheritanceLink (Concept "HolmesGrass") (Concept "Grass"))

; Sherlock Holmes and wet grass

; Rain
; P(R)
; true 0.2
; false 0.8

(EvaluationLink (stv 0.2 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "true")))


(EvaluationLink (stv 0.8 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Rain") (Concept "false")))


; Sprinkler
; P(S)
; switch-on  0.1
; switch-off 0.9

(EvaluationLink (stv 0.1 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-on")))

(EvaluationLink (stv 0.9 1)
 (PredicateNode "probability")
 (AssociativeLink (Concept "Sprinkler") (Concept "switch-off")))

; Watson grass
; P(WG|R)
; R      wet  dry
; true   1.0  0.0
; false  0.2  0.8

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "true" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

(EvaluationLink (stv 0.2 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.8 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AssociativeLink (Concept "Rain") (Concept "false" ))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

; Holmes grass
; P(HG|R)
; S          R      wet  dry
; switch-on  true   1.0  0.0
; switch-on  false  0.9  0.1
; switch-off true   1      0
; switch-off false  0      1

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

(EvaluationLink (stv 0.9 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-on" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry" (stv 0.1 1)))))

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "true" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

(EvaluationLink (stv 0.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off" ))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "wet"))))

(EvaluationLink (stv 1.0 1)
 (PredicateNode "probability")
 (ImplicationLink
  (AndLink
   (AssociativeLink (Concept "Sprinkler") (Concept "switch-off"))
   (AssociativeLink (Concept "Rain") (Concept "false" )))
  (AssociativeLink (Concept "WatsonGrass") (Concept "dry"))))

; P(HG=T|WG=T)

; Evidence: Watson grass is wet
; P(WG = T)
(EvaluationLink (stv 1.0 1)
 (PredicateNode "evidence")
 (AssociativeLink (Concept "WatsonGrass") (Concept "wet")))

; Evidence Holmes grass is wet
; P(HG = T)
(EvaluationLink (stv 1.0 1)
 (PredicateNode "evidence")
 (AssociativeLink (Concept "HolmesGrass") (Concept "wet")))

; Generate Factor Graph


; Sample

(EvaluationLink
 (PredicateNode "graph-edge")
 (AndLink (Concept "P4") (Concept "Rain" )))

(EvaluationLink
 (PredicateNode "graph-edge")
 (AndLink (Concept "P2") (Concept "Rain" )))

(EvaluationLink
 (PredicateNode "graph-edge")
 (AndLink (Concept "P2") (Concept "WatsonGrass" )))

(EvaluationLink
 (PredicateNode "factor-arguments-list")
 (ListLink
  (Concept "P4")
  (Concept "Rain")))

(EvaluationLink
 (PredicateNode "factor-arguments-list")
 (ListLink
  (Concept "P2")
  (Concept "Rain")
  (Concept "WatsonGrass")))


; Initial message from Variable to Factor

;; Initial message from WatsonGrass to P2
;(EvaluationLink
; (PredicateNode "graph-message")
; (AndLink
;  (Concept "WatsonGraph")
;  (Concept "P2")
;  (AndLink (Number "1") (Number "1"))))

;(EvaluationLink
; (PredicateNode "graph-message")
; (AndLink
;  (Concept "P2")
;  (Concept "Rain")
;  (AndLink
;   (Number "P2(Rain=false, WatsonGrass=dry) * 1 + P2(Rain=false, WatsonGrass=wet) * 1")
;   (Number "P2(Rain=true, WatsonGrass=dry) * 1 + P2(Rain=true, WatsonGrass=wet) * 1"))))


;(ImplicationScope
; (VariableList
;  (TypedVariable
;   (Variable "$F")
;   (Type "ConceptNode")
;  )
;  (TypedVariable
;   (Variable "$X")
;   (Type "ConceptNode")
;  )
; )
;
; (EvaluationLink
;  (PredicateNode "probability")
;  (AssociativeLink (Variable "$F") (Variable "$X")))
;
; (EvaluationLink
;  (PredicateNode "graph-edge")
;  (AssociativeLink (Variable "$F") (Variable "$X")))
;)
;
;(State (Anchor "sum-A") (Number 0))
;
;(Define (DefinedPredicate "counter")
; (True
; (Put
;  (State (Anchor "sum-A") (Variable "$x"))
;  (Plus (Number 1)
;   (Get (State (Anchor "sum-A") (Variable "$y")))))
; )
;)
;
;(display (cog-evaluate! (DefinedPredicate "counter")))
;(newline)
;(display (cog-evaluate! (DefinedPredicate "counter")))
;(newline)
