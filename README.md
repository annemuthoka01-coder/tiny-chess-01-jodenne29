# Tiny Chess 01 - Entry: `engine_golf6.py`

This repository contains our competition entry for `tiny-chess-01`. The engine is implemented in readable form in `engine_golf6.py` and packed into `main.py` for submission.

## Engine Architecture & Features

- **Search**: Alpha-beta minimax with iterative deepening and a strict node budget of **60,000 nodes** per move, ensuring completely deterministic behavior without clock dependency.
- **Quiescence Search**: Handles in-check nodes at horizon (`depth <= 0`) to prevent horizon effects on mating lines, and evaluates stand-pat / captures when out of check.
- **Transposition Table**: Stores entries as `(depth, value, flag, move)` supporting exact values, lower bounds (fail-high), and upper bounds (fail-low) with window adjustments on probe.
- **Move Ordering**: Prioritizes transposition table moves followed by MVV-LVA capture ordering.
- **Extensions**: Implements check extensions to prevent premature cutoff when a side to move is in check.
- **Evaluation**: Uses classic Piece-Square Tables (PSTs) combined with standard piece values.

## Packaging & Deployment

- **Source**: [`engine_golf6.py`](engine_golf6.py) contains the full uncompressed engine implementation and test harness.
- **Packed Binary**: [`main.py`](main.py) is compiled and compressed from `engine_golf6.py` using `makefun compress` (staying strictly within the 4,096-byte limit at **3,913 bytes**).
- **Driver**: Communicates with the competition server via the environment variable `MAKEFUN_ENV_URL` using `/game` and `/move` REST endpoints, complete with robust legal-move safety guards.

## Practice Result

- **Trial Outcome**: Verified practice trial-0 achieved **Elo 1279** (surpassing the qualifying floor of 1154).
- **Gauntlet Record**: 1 win, 4 draws, and 1 loss across the 6-game house gauntlet (all games successfully completed without timeout or illegal moves).
