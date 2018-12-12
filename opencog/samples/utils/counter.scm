(use-modules (opencog) (opencog query) (opencog exec))

; See original example:
; https://github.com/singnet/atomspace/blob/master/examples/atomspace/random-choice.scm

(State (Concept "counter-state") (Number 0))

(Define (DefinedPredicate "counter")
 (True
  (Put
   (State (Concept "counter-state") (Variable "$counter"))
   (Plus (Number 1)
    (Get (State (Concept "counter-state") (Variable "$counter-next")))))))

; Run Counter
(cog-evaluate! (DefinedPredicate "counter"))

; Print Counter
(display (cog-execute! (Get (State (Concept "counter-state") (Variable "$counter")))))
(newline)

; Run Counter
(cog-evaluate! (DefinedPredicate "counter"))

; Print Counter
(display (cog-execute! (Get (State (Concept "counter-state") (Variable "$counter")))))
(newline)
