<div align="center">
    <h2>Traffic Light Reinforcement Learning Environment</h2>
    <blockquote> Traffic light environment for Reinforcement Learning with Unity</blockquote>
</div>

- [1. Snapshot](#1-snapshot)
- [2. Technology](#2-technology)
- [3. Design](#3-design)
- [4. Branch](#4-branch)
- [5. Reference](#5-reference)

## 1. Snapshot
![image](https://user-images.githubusercontent.com/50461553/198821317-ee66b91b-0606-4161-82d2-16294be7eb4f.png)

## 2. Technology
- Unity: 2020.3.33f1
- ML-Agents: 0.28.0
- C#: 8.0
- Python: 3.9.6
- PyTorch: 1.12.1

## 3. Design
- Environment for testing Reinforcement Learning algorithms.
- Properties:

    | Property | Detail  |
    | -------- | --------|
    | Action Space | Discrete(8) |
    | Observation Shape | (12,)  |

    Observation space includes:
    - Waiting time of vehicles.
    - Speed of first car on each lane.
    - Timer for green lights.
    - Current state of traffic lights.

- Can be used for testing external algorithms or ML-Agents built-in algorithms.
- Includes built-in debug logs when using executable.

## 4. Branch
There are 2 branches for 2 versions of the environment:
- Reinforcement Learning: https://github.com/Spencer266/T-Juntion/tree/multi
- Fixed-time: https://github.com/Spencer266/T-Juntion/tree/linear

**Note**: The second one is used for comparing Reinforcement Learning and Fixed-time method. However, it can acts as a standalone own project.

## 5. Reference
- ML-Agents: https://github.com/Unity-Technologies/ml-agents