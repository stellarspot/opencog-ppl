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


; Using sets
; Apply variable for each value from the set
(display
 (cog-execute!
  (Put
   (Inheritance
    (Concept "ball")
    (Variable "$COLOR")
   )
   (Set
    (Concept "red")
    (Concept "blue")))))

; Filter values
; Filter out nodes that are not concepts
(display
 (cog-execute!
  (PutLink
   (TypedVariableLink
    (VariableNode "%x")
    (TypeNode "ConceptNode"))
   (VariableNode "%x")
   (SetLink
    (NumberNode "42")
    (ConceptNode "foo")
    (SchemaNode "finagle")
    (ConceptNode "bar")))))