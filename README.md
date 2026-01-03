# AI-Game-playing-agent
An intelligent game-playing agent for the River and Stones board game, implementing alpha–beta pruning with a rich heuristic evaluation function, advanced move generation, and strategic scoring optimization.

# About the Game: Rivers and Stones

Rivers and Stones is a two-player, turn-based strategic board game played on a rectangular grid of varying sizes (small, medium, and large boards). Each player controls identical pieces that can dynamically switch between two roles: Stone and River. Stones are used for scoring, while Rivers enable long-range, directional movement across the board 
The primary objective is to place a fixed number of stones (4–6, depending on board size) into the opponent’s scoring area before they do the same. Unlike traditional board games, pieces in Rivers and Stones are not static—players can move, push, flip, or rotate pieces, leading to a highly dynamic and tactical game environment 
A unique mechanic of the game is river flow movement: when a piece enters a River, it may travel multiple cells along the river’s orientation until blocked. Rivers can also be rotated or flipped, allowing players to reconfigure mobility paths during the game. Strategic pushing mechanics further allow repositioning of opponent pieces under strict constraints, adding depth to adversarial planning 
The combination of dual-purpose pieces, long-range movement via rivers, constrained pushing rules, and strict time limits makes Rivers and Stones an excellent testbed for adversarial AI techniques such as alpha–beta pruning, heuristic evaluation, and strategic search under time constraints.
