(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))


(Member (Concept "ball1") (Concept "basket1"))
(Member (Concept "ball2") (Concept "basket1"))

(Member (Concept "ball1") (Concept "basket2"))
(Member (Concept "ball2") (Concept "basket2"))

(Member (Concept "ball1") (Concept "basket3"))
(Member (Concept "ball3") (Concept "basket3"))

(define (balls-in-baskets basket)
 (Bind
  (TypedVariable (Variable "$BALL") (Type "ConceptNode"))
  (Member
   (Variable "$BALL")
   basket)
  (Variable "$BALL")))

(display
 (cog-execute!
  (balls-in-baskets (Concept "basket1"))))

(display
 (cog-execute!
  (balls-in-baskets (Concept "basket2"))))

(display
 (cog-evaluate!
  (Equal
   (balls-in-baskets (Concept "basket1"))
   (balls-in-baskets (Concept "basket2"))
  )))
(newline)

(display
 (cog-evaluate!
  (Equal
   (balls-in-baskets (Concept "basket1"))
   (balls-in-baskets (Concept "basket3"))
  )))
(newline)
