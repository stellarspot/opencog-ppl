(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

; Define a hypergraph called "human-implies-animal"
(define human-implies-animal
 (BindLink
  (VariableNode "$H")
  ; This is the pattern that will be matched ...
  (InheritanceLink
   (VariableNode "$H")
   (ConceptNode "human")
  )
  ; This is the hypergraph that will be created if the
  ; above pattern is found.
  (InheritanceLink
   (VariableNode "$H")
   (ConceptNode "animal"))))

; Some data to populate the atomspace:
(InheritanceLink (stv 1 1)  ; a non-zero truth value is needed!
 (ConceptNode "John")
 (ConceptNode "human"))

; Run the actual implication
(display (cog-execute! human-implies-animal))