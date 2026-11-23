# Tiny Chess (tiny-chess-01) v7

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
