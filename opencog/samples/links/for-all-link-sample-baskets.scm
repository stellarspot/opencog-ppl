(use-modules (opencog) (opencog query) (opencog exec))

(define fruite (Concept "Fruite"))
(define vegetable (Concept "Vegetable"))

(define apple (Concept "Apple"))
(define orange (Concept "Orange"))

(define potato (Concept "Potato"))
(define cucumber (Concept "Cucumber"))


(Inheritance apple fruite)
(Inheritance orange fruite)
(Inheritance potato vegetable)
(Inheritance cucumber vegetable)

(define basket1 (Concept "Basket 1"))
(define basket2 (Concept "Basket 2"))
(define basket3 (Concept "Basket 3"))

(Member apple basket1)
(Member orange basket1)

(Member apple basket2)
(Member potato basket2)

(Member potato basket2)
(Member cucumber basket2)


(define pattern
 (Bind
  (Variable "$X")
  (ForAll
   (Variable "$Y")
   (And
    (Member
     (Variable "$Y")
     (Variable "$X"))
    (Inheritance
     (Variable "$Y")
     fruite)))
  (Variable "$X")))


(display
 (cog-execute! pattern)
)