(use-modules (opencog) (opencog query) (opencog exec) (opencog rule-engine))

;;;;;;;;;;;;;;;;;;;;;
;;; Knowledge base ;;
;;;;;;;;;;;;;;;;;;;;;


(define R (ConceptNode "Rain"))
(define W (ConceptNode "Wet Grass"))

; R -> W
(Implication (stv 1 1) R W)

;;;;;;;;;;;;;;;;;;;;;;
;; Backward Chainer ;;
;;;;;;;;;;;;;;;;;;;;;;

(load "belief-propagation-ure-rules.scm")

(display
 (cog-bc
  belief-propagation-rbs

  (EvaluationLink
   graph-edge-predicate
   (ListLink (Variable "$X") W))

  #:vardecl (TypedVariable (Variable "$X") (TypeNode "ConceptNode")))
)