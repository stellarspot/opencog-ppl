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


(define (balls-from-basket basket)
 (Bind
  (TypedVariable (Variable "$BALL") (Type "ConceptNode"))
  (Member (Variable "$BALL") basket)
  (Variable "$BALL")))


(define (red-balls-from-basket basket)
 (Bind
  (TypedVariable (Variable "$BALL") (Type "ConceptNode"))
  (And
   (Member (Variable "$BALL") basket)
   (Inheritance (Variable "$BALL") (Concept "red")))
  (Variable "$BALL")))

(define baskets-with-all-red-balls
 (Bind
  (TypedVariable (Variable "$BASKET") (Type "ConceptNode"))
  (Equal
   (balls-from-basket (Variable "$BASKET"))
   (red-balls-from-basket (Variable "$BASKET")))
  (Variable "$BASKET")))


; Display balls
(display "balls from basket1:\n")
(display (cog-execute! (balls-from-basket (Concept "basket1"))))


(display "red balls from basket1:\n")
(display (cog-execute! (red-balls-from-basket (Concept "basket1"))))

(display "balls from basket2:\n")
(display (cog-execute! (balls-from-basket (Concept "basket2"))))


(display "red balls from basket2:\n")
(display (cog-execute! (red-balls-from-basket (Concept "basket2"))))

(display "balls from basket3:\n")
(display (cog-execute! (balls-from-basket (Concept "basket3"))))


(display "red balls from basket3:\n")
(display (cog-execute! (red-balls-from-basket (Concept "basket3"))))

(display "baskets with all red balls:\n")
(display (cog-execute! baskets-with-all-red-balls))


(define baskets-with-all-red-balls-in-one-request
 (Bind
  (TypedVariable (Variable "$BASKET") (Type "ConceptNode"))
  (Equal
   (Bind
    (TypedVariable (Variable "$BALL") (Type "ConceptNode"))
    (Member
     (Variable "$BALL")
     (Variable "$BASKET"))
    (Variable "$BALL"))
   (Bind
    (TypedVariable (Variable "$BALL") (Type "ConceptNode"))
    (And
     (Member
      (Variable "$BALL")
      (Variable "$BASKET"))
     (Inheritance
      (Variable "$BALL")
      (Concept "red")))
    (Variable "$BALL")))
  (Variable "$BASKET")))

(display "baskets with all red balls in one request:\n")
(display (cog-execute! baskets-with-all-red-balls-in-one-request))