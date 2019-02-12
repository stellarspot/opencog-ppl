(use-modules (opencog) (opencog exec))


(display
 (cog-execute!
  (Put
   (Plus
    (Number 2)
    (Variable "$X"))
   (Number 3))))


(display
 (cog-execute!
  (Put
   (Plus
    (Number 2)
    (Variable "$X")
    (Variable "$Y")
   )
   (List
    (Number 3)
    (Number 4)))))


(display
 (cog-execute!
  (Put
   (Inheritance
    (Variable "$BALL")
    (Variable "$COLOR")
   )
   (List
    (Concept "ball1")
    (Concept "green")))))