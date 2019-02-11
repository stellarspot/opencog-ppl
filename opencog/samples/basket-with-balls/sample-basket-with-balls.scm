(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;(use-modules (opencog logger))
;(cog-logger-set-level! "fine")


(Member (Concept "ball1") (Concept "basket1"))
(Member (Concept "ball2") (Concept "basket1"))

(Member (Concept "ball3") (Concept "basket2"))
(Member (Concept "ball4") (Concept "basket2"))

(Member (Concept "ball5") (Concept "basket3"))
(Member (Concept "ball6") (Concept "basket3"))

(Inheritance (Concept "ball1") (Concept "red"))
(Inheritance (Concept "ball2") (Concept "red"))
(Inheritance (Concept "ball3") (Concept "red"))
(Inheritance (Concept "ball4") (Concept "green"))
(Inheritance (Concept "ball5") (Concept "green"))
(Inheritance (Concept "ball6") (Concept "green"))


(define baskets-with-red-balls
 (Bind
  (VariableList
   (TypedVariable (Variable "$BASKET") (Type "ConceptNode"))
   (TypedVariable (Variable "$BALL") (Type "ConceptNode")))
  (And
   (Member
    (Variable "$BALL")
    (Variable "$BASKET"))
   (Inheritance
    (Variable "$BALL")
    (Concept "red")))
  (Variable "$BASKET")))

(display
 (cog-execute! baskets-with-red-balls)
)