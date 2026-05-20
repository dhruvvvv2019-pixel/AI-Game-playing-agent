## Rivers & Stones AI Agent
Strategic Game AI with Heuristic Search & Domain Optimization

## Overview

In this project, I designed and implemented an intelligent game-playing agent for the Rivers and Stones strategy game. The objective of the game is to place all my stone pieces into the opponent’s scoring area while leveraging river mechanics for long-range movement and tactical control .

Rather than relying on generic AI approaches, I focused on building a domain-aware, highly optimized agent that understands the game mechanics deeply, including river flow, pushing dynamics, and scoring constraints. My goal was to create an agent that prioritizes winning opportunities instead of blindly exploring the search space, while still maintaining a balance between offensive play, defensive positioning, and mobility. Given the strict time constraints imposed by the game, efficiency was a key design requirement throughout my implementation.

## Core Architecture

My implementation follows a modular design that separates game logic from decision-making. I built a set of utility functions that abstract core operations such as board copying, move validation, scoring detection, and river traversal. This abstraction allowed me to focus on the intelligence of the agent without repeatedly dealing with low-level rule enforcement.

At the heart of the system is a custom move generation engine. Instead of enumerating moves in a naive way, I implemented a structured approach that captures all legal actions while respecting the game’s constraints. A key component of this is the river flow simulation, where I used a BFS-style traversal to model how pieces move through chained river segments. This allows the agent to efficiently compute multi-hop movements, account for directional flow, and avoid invalid transitions such as entering the opponent’s scoring area.

The move generator also supports all action types defined by the game, including normal moves, pushes, flips, and rotations. Special care was taken to correctly model push mechanics, distinguishing between stone pushes and more complex river-based pushes that can span multiple cells. This ensures that the agent fully exploits the flexibility offered by river mechanics without violating game rules.

## Intelligent Move Prioritization

One of the most important design decisions in my implementation was to move away from treating all moves equally. Instead, I built a priority-driven move selection system that filters and ranks moves based on their strategic importance.

The agent first checks for immediate winning opportunities, such as completing the scoring area or flipping rivers into stones to secure victory. It then looks for direct scoring moves where a piece can enter the scoring zone in a single step, including push-based scenarios. Beyond that, it identifies river-assisted paths that can lead to scoring positions through chained movements, effectively exploiting the mobility advantage provided by rivers.

I also incorporated defensive filtering to avoid moves that would weaken critical positions or allow the opponent to gain easy access to scoring zones. Only when no high-priority moves are available does the agent fall back to exploring the broader move space. This approach significantly reduces the branching factor while ensuring that the agent remains focused on meaningful actions.

## Board Evaluation Strategy

To evaluate game states, I implemented a multi-layer heuristic function that combines positional, distance-based, and game-specific features. A major component of this evaluation is the use of precomputed positional matrices for both stones and rivers. These matrices are tailored for different board sizes and reward positions that offer strategic advantages, such as central control and proximity to scoring areas.

In addition to positional scoring, I incorporated Manhattan distance calculations to measure how close pieces are to their respective scoring zones. This helps the agent prioritize moves that accelerate progress toward the objective.

The evaluation function also captures domain-specific metrics such as the number of stones already in the scoring area, the number of rivers positioned advantageously, and pieces that are one move away from scoring. By combining these factors, the evaluation becomes highly context-aware and reflects the actual dynamics of the game rather than relying on simplistic heuristics.

## Search Strategy

The agent uses a depth-limited search with a depth of two, combined with strong heuristic guidance. Instead of attempting deep exhaustive search, which is computationally expensive given the complexity of the game, I focused on improving move ordering and pruning through prioritization.

This approach allows the agent to evaluate promising states quickly while avoiding unnecessary computation on irrelevant branches. Given the large branching factor introduced by river chaining and push mechanics, as well as the strict time limits per match , this tradeoff between depth and efficiency proved to be essential.

## Key Engineering Decisions

A key decision in my design was to avoid a purely Minimax-based approach. While Minimax guarantees optimality in theory, it becomes impractical in this setting due to the complexity of the move space and time constraints. Instead, I combined shallow search with strong heuristics and intelligent pruning to achieve a balance between performance and decision quality.

I also chose to implement priority-based move generation because most possible moves in the game are not strategically relevant. By filtering early and focusing only on high-impact actions, the agent is able to make faster and more informed decisions.

Another important choice was to incorporate heavy domain-specific heuristics. The unique mechanics of the game, such as river chaining and flexible push dynamics, cannot be captured effectively by generic evaluation functions. By embedding these insights directly into the evaluation and move generation logic, the agent gains a significant strategic advantage.

## Strengths of the Agent

The resulting agent demonstrates strong domain awareness and is able to make efficient decisions under tight time constraints. It prioritizes offensive opportunities effectively while maintaining a reasonable level of defensive awareness. The use of heuristic pruning significantly reduces the search space, allowing the agent to focus on moves that are most likely to impact the outcome of the game.

## Limitations & Future Improvements

While the current implementation performs well, there are several areas for improvement. The search depth is fixed and does not adapt based on the game state or available time. The absence of alpha-beta pruning means that some unnecessary branches are still explored. Additionally, the agent does not explicitly model opponent behavior, which limits its ability to anticipate and counter advanced strategies.

In the future, I plan to extend this work by incorporating alpha-beta pruning and iterative deepening to improve search efficiency. I am also interested in integrating opponent-aware evaluation and exploring learning-based approaches for tuning heuristics. A potential long-term direction is to combine this framework with Monte Carlo Tree Search to further enhance decision-making under uncertainty.

## Below are the exact steps I followed to run this project from scratch on my laptop:

# 1. Clone the Repository

Open Command Prompt / Terminal and run:

git clone <GITHUB_REPO_URL>
cd AI-GAME-PLAYING-BOT

This downloads the project and moves into the project directory.

# 2. Check Python Installation

This project requires Python 3.x.

Check installed version:

python --version

or

python3 --version

Recommended:

Python 3.10 / 3.11 / 3.12

Avoid:
Python 3.14+ (causes pygame compatibility issues)

# 3. Create Virtual Environment

I created a virtual environment to isolate project dependencies.

Run:

python -m venv venv

This creates a local Python environment inside the project.

# 4. Activate Virtual Environment
Windows CMD
venv\Scripts\activate
Windows PowerShell
.\venv\Scripts\Activate.ps1
Mac / Linux
source venv/bin/activate

If successful, terminal should show:
(venv)

# 5. Upgrade pip (Recommended)
python -m pip install --upgrade pip setuptools wheel
This avoids package installation issues.

# 6. Install Dependencies
Run:
pip install -r requirements.txt

This installs:

pygame
flask
flask-socketio
requests
numpy
scipy
python-socketio

# 7. Verify Installation

Check if major packages are installed:
pip list

# 8. Run the Game Engine

This project supports multiple execution modes.

# Option A — AI vs AI (Recommended)

This is the easiest way to test the bot.

Run:

python gameEngine.py --mode aivai --circle random --square student

Meaning:
aivai → AI vs AI
circle random → Circle player uses random agent
square student → Square player uses my AI

This launches GUI mode.

# Option B — AI vs AI (CLI / No GUI)

If GUI causes pygame/display issues:
python gameEngine.py --mode aivai --circle random --square student --nogui

Runs in terminal only.

# Option C — Human vs AI

To manually play against the AI:

python gameEngine.py --mode hvai

This starts Human vs AI.

# 9. Run AI on Opposite Side (Testing Symmetry)

To test whether my agent behaves correctly as Circle:
python gameEngine.py --mode aivai --circle student --square random

Useful for validating side-specific heuristics.

# 10. Run Self-Play (AI vs AI)

To test my AI against itself:
python gameEngine.py --mode aivai --circle student --square student

This helps verify:
stability
legal moves
river behavior
scoring logic
strategic consistency

# 11. Run Different Board Sizes

Supported sizes:
small
medium
large

Example:
python gameEngine.py --mode aivai --board-size medium

# 12. Run Full Web-Based System (Optional)

This project also supports a distributed setup.
Start Server:

Mac/Linux/Git Bash:

bash start_server.sh 8080

Windows CMD:

python web_server.py 8080
Start Bot Clients

Open 2 terminals.

Terminal 1
python bot_client.py circle 8080 --strategy student
Terminal 2
python bot_client.py square 8080 --strategy student
Open Browser

Visit:
http://localhost:8080

Then create/start game.

## Conclusion

This project reflects my approach to practical AI system design, where the focus is not just on applying standard algorithms but on adapting them to the specific problem domain. I emphasized making informed tradeoffs between optimality and performance, designing an agent that is both efficient and strategically effective.

The final result is an AI agent that is not only capable of playing the game competitively but also demonstrates a thoughtful integration of algorithmic techniques, domain knowledge, and system-level optimization.
