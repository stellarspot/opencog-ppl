(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; PLN with Probabilities

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))

; Grass
(ImplicationLink (stv 0.8 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.2 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.1 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.9 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "dry")))

(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "wet"))))

(display (cog-tv (Associative (Concept "Grass") (Concept "wet"))))
(newline)