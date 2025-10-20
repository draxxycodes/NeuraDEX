; ====================================================================
; Risk Assessment Knowledge Base (Final, Corrected, Fact-Based)
; ====================================================================

; This file contains only simple, undeniable facts.
; The Python agent will query these facts to perform its reasoning.

; Fact: Define which symbols are considered high-volatility.
(= (volatility-of SHIB) (VolHigh))

; We don't need facts for low-volatility assets like BTC or ETH.
; The absence of a (VolHigh) fact is sufficient for the agent to
; know they are not high-risk in this context.