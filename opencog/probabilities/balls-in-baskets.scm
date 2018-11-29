(use-modules (opencog) (opencog query) (opencog exec))

; Baskets
(ConceptNode "basket1")
(ConceptNode "basket2")
; Balls

(ConceptNode "red-ball")
(ConceptNode "green-ball")
(ConceptNode "blue-ball")

; Basket1
(EvaluationLink (PredicateNode "contains")
 (ListLink (ConceptNode "basket1") (ConceptNode "red-ball") (NumberNode "1")))

(EvaluationLink (PredicateNode "contains")
 (ListLink (ConceptNode "basket1") (ConceptNode "green-ball") (NumberNode "2")))

; Basket2
(EvaluationLink (PredicateNode "contains")
 (ListLink (ConceptNode "basket2") (ConceptNode "red-ball") (NumberNode "3")))

(EvaluationLink (PredicateNode "contains")
 (ListLink (ConceptNode "basket2") (ConceptNode "green-ball") (NumberNode "4")))

(EvaluationLink (PredicateNode "contains")
 (ListLink (ConceptNode "basket2") (ConceptNode "blue-ball") (NumberNode "5")))


(DefineLink
 (DefinedSchemaNode "number-of-balls-in-basket")
 (LambdaLink
  (VariableList
   (VariableNode "$BASKET")
   (VariableNode "$BALL"))
  (BindLink
   (VariableNode "$NUM")
   (EvaluationLink (PredicateNode "contains")
    (ListLink (VariableNode "$BASKET") (VariableNode "$BALL") (Variable "$NUM"))
   )
   (Variable "$NUM")
  )
 )
)


(display "number of green balls in busket 1")
(newline)
(display
 (cog-execute!
  (PutLink
   (DefinedSchemaNode "number-of-balls-in-basket")
   (ListLink
    (ConceptNode "basket1")
    (ConceptNode "green-ball")
   )
  )
 )
)

(display "number of green balls in busket 2")
(newline)
(display
 (cog-execute!
  (PutLink
   (DefinedSchemaNode "number-of-balls-in-basket")
   (ListLink
    (ConceptNode "basket2")
    (ConceptNode "green-ball")
   )
  )
 )
)
