(use-modules (opencog) (opencog exec))

(display
 (cog-evaluate!
  (Equal
   (Set)
   (Set))))

(newline)

(display
 (cog-evaluate!
  (Equal
   (Set (Concept "Cat"))
   (Set))))

(newline)

(display
 (cog-evaluate!
  (Equal
   (Set (Concept "Cat"))
   (Set (Concept "Cat")))))

(newline)

(display
 (cog-evaluate!
  (Equal
   (Set (Concept "Cat") (Concept "Dog"))
   (Set (Concept "Dog") (Concept "Cat")))))

(newline)
