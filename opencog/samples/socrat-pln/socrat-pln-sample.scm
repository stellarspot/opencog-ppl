(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

(InheritanceLink (stv 0.8 0.9) (Concept "Socrates") (Concept "man"))
(InheritanceLink (stv 0.98 0.94) (Concept "man") (Concept "mortal"))

(display
 (cog-bc
  (ConceptNode "PLN")
  (InheritanceLink (VariableNode "$who") (ConceptNode "mortal"))
  #:vardecl (TypedVariableLink (VariableNode "$who") (TypeNode "ConceptNode"))))

