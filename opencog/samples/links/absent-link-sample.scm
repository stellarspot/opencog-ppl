(use-modules (opencog) (opencog query) (opencog exec))

(define cat (Concept "cat"))
(define dog (Concept "dog"))
(define pet (Concept "pet"))
(define animal (Concept "animal"))

(Inheritance cat animal)

(define (pattern what)
 (Bind
  (Variable "$X")
  (Absent
   (Inheritance
    (Variable "$X")
    what)
  )
  (Variable "$X")))


(display
 (cog-execute! (pattern animal)))

(display
 (cog-execute! (pattern pet)))
