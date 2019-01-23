(use-modules (opencog) (opencog exec) (opencog query))

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;

(Product (stv 1 1) ; a non-zero truth value is needed!
 (ConceptNode "A")
 (ConceptNode "B"))

;;;;;;;;;;;;;;;;;
;; Rule  base  ;;
;;;;;;;;;;;;;;;;;

(define (on-top h)
 (display "on-top input:\n")
 (display h)
 (cog-set-tv! h (cog-new-stv 0.75 0.42))
 h)

(define on-top-rule
 (BindLink
  (VariableList
   (GlobNode "$X1")
   (TypedVariable (Variable "$X2") (Type "ConceptNode"))
  )
  (Product
   (GlobNode "$X1")
   (Variable "$X2")
  )
  (ExecutionOutputLink
   (GroundedSchemaNode "scm: on-top")
   (ListLink
    (Product
     (Variable "$X2")
     (GlobNode "$X1")
    )))))


(display (cog-execute! on-top-rule))