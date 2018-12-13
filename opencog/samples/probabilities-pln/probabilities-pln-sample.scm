(use-modules (opencog) )

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; PLN with Probabilities

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))


; Grass
(ImplicationLink (stv 0.8 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "true")))

(ImplicationLink (stv 0.2 1)
 (Associative (Concept "Rain") (Concept "true"))
 (Associative (Concept "Grass") (Concept "false")))

(ImplicationLink (stv 0.1 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "true")))

(ImplicationLink (stv 0.9 1)
 (Associative (Concept "Rain") (Concept "false"))
 (Associative (Concept "Grass") (Concept "false")))

(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "true"))
 ))
