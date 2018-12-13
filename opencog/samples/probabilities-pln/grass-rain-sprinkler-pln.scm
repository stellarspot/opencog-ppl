(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

(load "/home/opencog/share/opencog/opencog/pln/pln-config.scm")

; Rain
(Associative (stv 0.2 1) (Concept "Rain") (Concept "true"))
(Associative (stv 0.8 1) (Concept "Rain") (Concept "false"))

; Sprinkler
(Associative (stv 0.4 1) (Concept "Sprinkler") (Concept "on"))
(Associative (stv 0.6 1) (Concept "Sprinkler") (Concept "off"))

; Grass
(ImplicationLink (stv 0.9 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.1 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.8 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.2 1)
 (And
  (Associative (Concept "Rain") (Concept "true"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.6 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.3 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "on")))
 (Associative (Concept "Grass") (Concept "dry")))

(ImplicationLink (stv 0.1 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "wet")))

(ImplicationLink (stv 0.9 1)
 (And
  (Associative (Concept "Rain") (Concept "false"))
  (Associative (Concept "Sprinkler") (Concept "off")))
 (Associative (Concept "Grass") (Concept "dry")))

(display (cog-tv (Associative (Concept "Grass") (Concept "wet"))))

; Call PLN
(display
 (cog-bc
  (ConceptNode "PLN")
  (Associative (Concept "Grass") (Concept "wet"))))

(display (cog-tv (Associative (Concept "Grass") (Concept "wet"))))
(newline)