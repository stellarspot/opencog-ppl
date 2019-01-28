(use-modules (opencog) (opencog query) (opencog exec))

(define cat (Concept "cat"))
(define stone (Concept "stone"))
(define animal (Concept "animal"))

(Inheritance cat animal)

(define pattern
 (Bind
  (Variable "$X")
  (Absent
   (Inheritance
    (Variable "$X")
    animal))
  (Variable "$X")))


(display
 (cog-execute! pattern))
