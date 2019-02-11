(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))


(display
 (cog-execute!
  (Plus (Number 1) (Number 2))))