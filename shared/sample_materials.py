"""
Sample academic study materials for StudySync demonstration and RAG indexing.
Includes authoritative course notes for DBMS, Operating Systems, Computer Networks, and DSA.
"""

from pathlib import Path


SAMPLE_MATERIALS = {
    "dbms_transactions.txt": """
# Database Management Systems: Transactions and Concurrency Control

## 1. Transaction Concept and ACID Properties
A transaction is a logical unit of database processing that includes one or more database access operations. To ensure database integrity, transactions must satisfy the ACID properties:
- **Atomicity**: The "all-or-nothing" rule. Either all operations of the transaction are reflected properly in the database, or none are. This is typically managed by the recovery manager using Write-Ahead Logging (WAL).
- **Consistency**: Execution of a transaction in isolation preserves database consistency. Any transaction must transform the database from one valid state satisfying all invariants to another.
- **Isolation**: Even though multiple transactions may execute concurrently, each transaction must remain unaware of concurrently executing transactions. Isolation levels define the degree to which a transaction is exposed to uncommitted changes: Read Uncommitted, Read Committed, Repeatable Read, and Serializable.
- **Durability**: Once a transaction commits, the changes it has made to the database persist, even if system crashes occur immediately afterwards.

## 2. Serializability and Conflict Serializability
A schedule is a sequence of the operations performed by concurrent transactions. A schedule is serial if transactions execute one after another without interleaving.
A schedule is conflict serializable if it is conflict equivalent to a serial schedule. Two operations conflict if:
1. They belong to different transactions.
2. They access the same data item.
3. At least one of the operations is a write operation.
Conflict serializability is verified by constructing a precedence graph (or serialization graph). If the graph contains no directed cycles, the schedule is conflict serializable.

## 3. Two-Phase Locking (2PL) Protocol
Two-Phase Locking is a concurrency control protocol that guarantees conflict serializability:
1. **Growing Phase**: A transaction may acquire locks of data items, but cannot release any lock.
2. **Shrinking Phase**: A transaction may release locks, but cannot acquire any new lock.
Strict 2PL requires all exclusive locks to be held until the transaction commits or aborts, preventing cascading rollbacks (cascadeless schedules).
Rigorous 2PL requires both shared and exclusive locks to be held until transaction termination.

## 4. Normalization and Normal Forms
Normalization is the process of organizing attributes in a relational database to minimize data redundancy and prevent insertion, update, and deletion anomalies.
- **First Normal Form (1NF)**: Every column contains only atomic (indivisible) values, and each record is unique.
- **Second Normal Form (2NF)**: Must be in 1NF, and all non-prime attributes must be fully functionally dependent on the entire primary key (no partial dependencies).
- **Third Normal Form (3NF)**: Must be in 2NF, and no non-prime attribute is transitively dependent on the candidate key. (Formally, for every X -> Y, X is a superkey or Y is a prime attribute).
- **Boyce-Codd Normal Form (BCNF)**: A stricter version of 3NF. For every non-trivial functional dependency X -> Y, X must be a superkey.
""",

    "os_process_synchronization.txt": """
# Operating Systems: Process Synchronization, Deadlocks, and CPU Scheduling

## 1. The Critical-Section Problem and Semaphores
When multiple concurrent processes share system resources or memory, race conditions can occur if execution order is arbitrary. The critical section is a segment of code where shared resources are modified. Any valid solution to the critical section problem must satisfy three essential criteria:
1. **Mutual Exclusion**: If process P_i is executing in its critical section, no other processes can be executing in their critical sections.
2. **Progress**: If no process is executing in its critical section and some processes wish to enter, only those processes not in their remainder section can participate in deciding which will enter next, and this selection cannot be postponed indefinitely.
3. **Bounded Waiting**: There must exist a bound on the number of times that other processes are allowed to enter their critical sections after a process has made a request and before that request is granted.

A **Semaphore** is a synchronization tool consisting of an integer variable accessed only through two standard atomic operations: wait() (also known as P) and signal() (also known as V).
- Counting semaphores have an unrestricted range.
- Binary semaphores (mutex locks) take values 0 or 1.

## 2. Deadlocks: Characterization and Prevention
A deadlock occurs when a set of concurrent processes are permanently blocked because each process is holding a resource and waiting for another resource acquired by some other process in the set.
A deadlock can arise if and only if the four Coffman conditions hold simultaneously:
1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode.
2. **Hold and Wait**: A process must currently hold at least one resource and be waiting to acquire additional resources held by other processes.
3. **No Preemption**: Resources cannot be preempted; a resource can be released only voluntarily by the process holding it after that process has completed its task.
4. **Circular Wait**: A closed chain of processes exists such that each process holds at least one resource needed by the next process in the chain.

Deadlock Prevention systematically invalidates at least one of these four conditions (e.g., imposing total resource ordering eliminates Circular Wait).
Deadlock Avoidance uses dynamic state analysis, such as Dijkstra's **Banker's Algorithm**, to ensure the system never enters an unsafe state.

## 3. CPU Scheduling Algorithms
CPU scheduling algorithms determine which process in the ready queue is allocated the CPU core:
- **First-Come, First-Served (FCFS)**: Non-preemptive, susceptible to the convoy effect.
- **Shortest Job First (SJF)**: Optimal average waiting time; preemptive variant is Shortest Remaining Time First (SRTF).
- **Round Robin (RR)**: Preemptive, uses a fixed time quantum; optimal for time-sharing interactive systems.
- **Priority Scheduling**: Processes scheduled by priority value; susceptible to starvation (solved using aging).
""",

    "dsa_dynamic_programming.txt": """
# Data Structures and Algorithms: Dynamic Programming and Graph Algorithms

## 1. Principles of Dynamic Programming (DP)
Dynamic Programming is an algorithmic paradigm that solves complex optimization problems by breaking them down into overlapping subproblems and optimal substructure.
- **Optimal Substructure**: An optimal solution to the overall problem contains within it optimal solutions to subproblems.
- **Overlapping Subproblems**: The recursive algorithm visits the same subproblems repeatedly rather than generating new subproblems at each stage.

There are two primary paradigms to implement DP:
1. **Top-Down with Memoization**: Start solving the problem recursively from the main problem. Before computing a subproblem, check a hash map or table; if already computed, return the cached result.
2. **Bottom-Up with Tabulation**: Solve base cases first and sequentially populate a table from smaller subproblems up to the target state. Usually eliminates recursion call-stack overhead.

Canonical problems include:
- 0/1 Knapsack Problem: State `dp[i][w] = max(dp[i-1][w], dp[i-1][w-val[i]] + cost[i])`
- Longest Common Subsequence (LCS): `dp[i][j] = dp[i-1][j-1] + 1` if match, else `max(dp[i-1][j], dp[i][j-1])`
- Matrix Chain Multiplication: Minimizing scalar multiplications through interval dynamic programming.

## 2. Graph Traversal and Shortest Path Algorithms
Graphs $G = (V, E)$ represent networks of nodes and relationships:
- **Breadth-First Search (BFS)**: Uses a Queue (FIFO); explores neighbor vertices level-by-level; computes shortest path on unweighted graphs. Time complexity: $O(V + E)$.
- **Depth-First Search (DFS)**: Uses a Stack or recursion; explores path as deeply as possible before backtracking; useful for topological sort, cycle detection, and strongly connected components (Kosaraju's / Tarjan's algorithms). Time complexity: $O(V + E)$.
- **Dijkstra's Algorithm**: Single-source shortest path for non-negative edge weights using a Min-Priority Queue. Time complexity: $O((V + E) \log V)$.
- **Bellman-Ford Algorithm**: Handles graphs with negative edge weights and detects negative weight cycles by relaxing all edges $V - 1$ times. Time complexity: $O(V \times E)$.
"""
}


def dump_sample_materials(target_dir: Path):
    """Save the sample textbook and lecture files to disk."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in SAMPLE_MATERIALS.items():
        p = target_dir / filename
        p.write_text(content.strip(), encoding="utf-8")
