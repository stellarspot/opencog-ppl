(use-modules (opencog) (opencog query) (opencog exec))

(define key (Predicate "legs-number"))
(define (legs-number who legs)
 (Evaluation key who (Number legs)))

; Mamalia
(define mammalia (Concept "mammalia"))
(define cat (Concept "cat"))
(define dog (Concept "dog"))

(Inheritance cat mammalia)
(Inheritance dog mammalia)
(legs-number cat 4)
(legs-number dog 4)

; Insect
(define insect (Concept "insect"))
(define ant (Concept "ant"))

(Inheritance ant insect)
(legs-number ant 6)

; Dragon
(define dragon (Concept "dragon"))
(define wyvern (Concept "wyvern"))
(define western-style-dragon (Concept "Western Style Dragon"))

(Inheritance wyvern dragon)
(Inheritance western-style-dragon dragon)
(legs-number wyvern 2)
(legs-number western-style-dragon 4)


; Find $X that
; For All (Inheritance $Y $X)
; (legs-number $Y 4)

;(define pattern
; (Bind
;  (Variable "$X")
;  (ForAll
;   (Variable "$Y")
;   (And
;    (Inheritance
;     (Variable "$Y")
;     (Variable "$X"))
;    (Evaluation
;     key
;     (Variable "$Y")
;     (NumberNode 4))))
;  (Variable "$X")))


; See discussion
; https://github.com/opencog/atomspace/issues/2018
(define pattern
 (Bind
  ;; Search requires two variables
  (VariableList (Variable "$X") (Variable "$Y"))
  (And
   (Inheritance (Variable "$Y") (Variable "$X"))
   (Evaluation key (Variable "$Y") (NumberNode 4)))

  ;; Return one of the two variables
  (Variable "$Y")))

(display
 (cog-execute! pattern)
)