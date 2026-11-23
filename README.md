# Tiny Chess (tiny-chess-01) v7

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/annemuthoka01-coder/tiny-chess-01-jodenne29/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/annemuthoka01-coder/tiny-chess-01-jodenne29/reward.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Tiny Chess is an ultra-compact, high-performance UCI-compatible chess engine written in pure Python, engineered specifically for extreme code golf and robust tactical search performance.

## Version 7 Features

- **Advanced Search**: Alpha-beta pruning with transposition table (TT) bound flags, killer move heuristics, null-move pruning, late move reduction (LMR), check extensions, and in-check quiescence search.
- **Tapered Endgame Evaluation**: Sophisticated phase-blended pawn and king evaluation tables (EGP/EGT) with bishop pair evaluation, ensuring smooth transitions from opening to endgame.
- **Deterministic Node Budget**: Fully deterministic node-budget taper based purely on game ply (`plies = (int(fen.split()[5]) - 1) * 2 + (1 if fen.split()[1] == 'b' else 0)`):
  - Ply < 50: 150,000 nodes
  - Ply 50–89: 100,000 nodes
  - Ply ≥ 90: 60,000 nodes
- **Fixed-Node Iterative Deepening**: Iterative deepening search up to depth 12 controlled strictly by the position-derived node budget—independent of external wall clocks for 100% replay reproducibility.

## Architecture & Code Golf

Designed to fit within strict size limits while maintaining high search depth and perft accuracy (perft depth 3 = 8,902 on startpos, 97,862 on Kiwipete). The codebase employs aggressive Python minification and data packing techniques to deliver competitive tournament-grade move selection in a tiny footprint.

## Measured Results

- **Packed Size**: `main.py` is packed at exactly 4,085 bytes (kit compress).
- **Local Practice Trial-0**: Scored 4.5/6 (3 wins, 3 draws, 0 losses) against the six calibrated house engines using the server's practice trial harness.
- **Local Elo Estimate**: 1,545 (up from the previous entry's 1,279).
- **Benchmark Speed**: Roughly 29,000–30,000 nodes per second.
- **Determinism**: Fully deterministic via fixed node budgets (no clocks).
