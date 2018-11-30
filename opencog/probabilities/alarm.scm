(use-modules (opencog) (opencog query) (opencog exec))

(use-modules (opencog logger))
(cog-logger-set-level! "debug")

(ConceptNode "event")
(ConceptNode "no-event")
(ConceptNode "earthquake")
(ConceptNode "burglary")

; TBD: use to define no-event probability
;(InheritanceLink (ConceptNode "no-event") (ConceptNode "event"))
;(InheritanceLink (ConceptNode "earthquake") (ConceptNode "event"))
;(InheritanceLink (ConceptNode "burglary") (ConceptNode "event"))

(EvaluationLink
 (PredicateNode "probability")
 (ListLink
  (ConceptNode "burglary")
  ; TBD Use RandomStream value
  (NumberNode "0.001")))

(EvaluationLink
 (PredicateNode "probability")
 (ListLink
  (ConceptNode "earthquake")
  ; TBD Use RandomStream value
  (NumberNode "0.002")))

; TBD Calculate as 1 - (p(burglary) + p(earthquake))
(EvaluationLink
 (PredicateNode "probability")
 (ListLink
  (ConceptNode "no-event")
  (NumberNode "0.97")))

(EvaluationLink
 (PredicateNode "conditional-probability")
 (ListLink
  (ConceptNode "alarm")
  (ConceptNode "burglary")
  (NumberNode "0.95")))

(EvaluationLink
 (PredicateNode "conditional-probability")
 (ListLink
  (ConceptNode "alarm")
  (ConceptNode "earthquake")
  (NumberNode "0.3")))

(EvaluationLink
 (PredicateNode "conditional-probability")
 (ListLink
  (ConceptNode "alarm")
  (ConceptNode "no-event")
  (NumberNode "0.01")))

(DefineLink
 (DefinedSchemaNode "event-probability")
 (LambdaLink
  (Variable "$EVENT")
  (BindLink
   (Variable "$PROBABILITY")
   (EvaluationLink
    (PredicateNode "probability")
    (ListLink
     (Variable "$EVENT")
     (Variable "$PROBABILITY")))
   (Variable "$PROBABILITY")
  )
 )
)

(DefineLink
 (DefinedSchemaNode "event-probability-set")
 (LambdaLink
  (Variable "$E")
  (BindLink
   (VariableList
    (Variable "$EVENT")
    (Variable "$P")
   )
   (EvaluationLink
    (PredicateNode "conditional-probability")
    (ListLink
     (Variable "$E")
     (Variable "$EVENT")
     (Variable "$P")))
   (TimesLink
    (Variable "$P")
    (PutLink
     (DefinedSchemaNode "event-probability")
     (Variable "$EVENT"))
   )
  )
 )
)

(DefineLink
 (DefinedSchemaNode "calculate-event-probability")
 (LambdaLink
  (Variable "$EVENT")
  (PlusLink
   (PutLink
    (DefinedSchemaNode "event-probability-set")
    (Variable "$EVENT")
   )
  )
 )
)

; Output
(display "probability of alarm")
(newline)

(display
 (cog-execute!
  (PutLink
   (DefinedSchemaNode "calculate-event-probability")
   (ConceptNode "alarm"))))