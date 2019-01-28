(use-modules (opencog) (opencog query) (opencog exec))

(define cat (Concept "cat"))
(define dog (Concept "cat"))
(define animal (Concept "animal"))
(define pet (Concept "pet"))


(Inheritance cat animal)
(Inheritance cat pet)

(Inheritance dog animal)


; ForAllLink throws exception
; [ERROR] Either incorrect or not implemented yet. Cannot evaluate (ForAllLink
(define test
 ;  (ForAll
 (Satisfaction
  (Variable "$X")
  (And
   (Inheritance
    (Variable "$X")
    animal)
   (Inheritance
    (Variable "$X")
    pet))))

(display
 (cog-evaluate! test)
)
(newline)