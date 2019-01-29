(use-modules (opencog) (opencog query) (opencog exec))
; See https://github.com/opencog/atomspace/issues/2017

(define cat (Concept "cat"))
(define stone (Concept "stone"))
(define animal (Concept "animal"))

(Inheritance cat animal)

(define pattern
 (Bind
  (TypedVariable
   (Variable "$X")
   (Type "ConceptNode"))
  (And
   (Absent
    (Inheritance
     (Variable "$X")
     animal))
   (Present
    (Variable "$X")))
  (Variable "$X")))


(display
 (cog-execute! pattern))
