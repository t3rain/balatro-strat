# Optimal Strategy for Balatro

## Motivation

Balatro strategies, atleast for me, are completely decided by the first few blinds. They are also the most vanilla, since you're most likely without jokers or score modifiers and are forced to resort to optimal strategies. Your score (and a lot of luck) here generally decides the fate of the rest of the game, as building up a a bigger bankroll or stacking powerful jokers can then guide you to hunt strategies that maximize their output. The point of this project is to see what happens in the initial vanilla blinds. 

My goto strategy for clearing such blinds is to hunt for flushes. This made sense to me intuitively 
since they seemed easier to complete. The goal of this project is to test this intuition, and see how often such a strategy clears a blind. Is there a better policy that can come close to near-optimal play?


## Rules and Assumptions

The state at any point the current hand, the remaining deck, hands left, discards left, and chips still needed
to reach the target, together with a fixed scoring configuration (base chips and mult
per hand type). Jokers, enhancements or boss effects will not be touched upon, atleast in the initial phase.

1. 


