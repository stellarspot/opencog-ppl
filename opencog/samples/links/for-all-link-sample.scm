(use-modules (opencog) (opencog query) (opencog exec))

(define cat (Concept "cat"))
(define dog (Concept "dog"))
(define mammalia (Concept "mammalia"))

(define ant (Concept "ant"))
(define insect (Concept "insect"))

(define key (Predicate "legs-number"))

(define (legs-number who legs)
 (Evaluation key who (Number legs)))

(Inheritance cat mammalia)
(Inheritance dog mammalia)
(legs-number cat 4)
(legs-number dog 4)

(Inheritance ant insect)
(legs-number ant 6)


; Find $X that
; For All (Inheritance $Y $X)
; (legs-number $Y 4)

(define pattern
 (Bind
  (Variable "$X")
  (ForAll
   (Variable "$Y")
   (And
    (Inheritance
     (Variable "$Y")
     (Variable "$X"))
    (Evaluation
     key
     (Variable "$Y")
     (NumberNode 4))))
  (Variable "$X")))

(display
 (cog-execute! pattern)
)