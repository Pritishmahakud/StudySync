// KIIT University - School of Computer Engineering (SCE)
// Comprehensive B.Tech Computer Science & Engineering (CSE) Curriculum & PYQ Bank

export interface PYQQuestion {
  qNo: number
  text: string
  marks: number
  module: string
  suggestedAnswerSnippet?: string
}

export interface PYQPaper {
  id: string
  examType: 'Mid-Semester' | 'End-Semester'
  year: number
  session: 'Autumn' | 'Spring'
  duration: string
  totalMarks: number
  questions: PYQQuestion[]
}

export interface CourseSubject {
  code: string
  title: string
  shortTitle: string
  category: 'Core' | 'Lab' | 'Elective' | 'Project' | 'Basic Sciences'
  credits: number
  semester: number
  topic: string
  modules: string[]
  progress: number
  rating: string
  time: string
  color: 'mint' | 'peach' | 'lavender' | 'blue' | 'rose'
  icon: string
  next: string
  description: string
  pyqs: PYQPaper[]
}

export interface SemesterData {
  semester: number
  label: string
  stage: string
  session: string
  isCurrent?: boolean
  courses: CourseSubject[]
}

export const KIIT_CURRICULUM: SemesterData[] = [
  {
    semester: 1,
    label: "Semester 1",
    stage: "Freshman",
    session: "Autumn Session",
    courses: [
      {
        code: "CS 1001",
        title: "Programming in C",
        shortTitle: "C Programming",
        category: "Core",
        credits: 4,
        semester: 1,
        topic: "Pointers · Dynamic Memory · Recursion · Structs",
        modules: [
          "Module 1: Introduction to Algorithms & Flowcharts",
          "Module 2: Control Structures & Iteration",
          "Module 3: Functions, Recursion & Variable Scope",
          "Module 4: Arrays, Strings & Pointer Arithmetic",
          "Module 5: Dynamic Memory Allocation (malloc, calloc, realloc, free)",
          "Module 6: Structures, Unions & File Handling"
        ],
        progress: 100,
        rating: "4.9",
        time: "14 min",
        color: "mint",
        icon: "▤",
        next: "Dynamic Memory Allocation & Pointers",
        description: "Foundational procedural programming using ANSI C with deep focus on memory layout and pointers.",
        pyqs: [
          {
            id: "CS1001-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Explain difference between pass by value and pass by reference in C with code examples.", marks: 5, module: "Functions" },
              { qNo: 2, text: "Write a recursive function to find the sum of digits of a positive integer.", marks: 5, module: "Recursion" },
              { qNo: 3, text: "Differentiate between malloc() and calloc(). Explain how dangling pointers occur.", marks: 10, module: "Dynamic Memory" }
            ]
          },
          {
            id: "CS1001-END-2024",
            examType: "End-Semester",
            year: 2024,
            session: "Autumn",
            duration: "3 Hours",
            totalMarks: 100,
            questions: [
              { qNo: 1, text: "Explain bitwise operators in C and write a C program to swap two numbers using XOR.", marks: 10, module: "Operators" },
              { qNo: 2, text: "Write a program using structures to store student details (Roll, Name, CGPA) and sort by CGPA.", marks: 15, module: "Structures" },
              { qNo: 3, text: "Explain file opening modes in C (r, w, a, r+, w+). Write a program to count words in a text file.", marks: 15, module: "File I/O" }
            ]
          }
        ]
      },
      {
        code: "MA 1001",
        title: "Mathematics - I",
        shortTitle: "Calculus & Linear Algebra",
        category: "Basic Sciences",
        credits: 4,
        semester: 1,
        topic: "Calculus · Ordinary Differential Eq · Matrices",
        modules: [
          "Module 1: Differential Calculus & Rolle's / Mean Value Theorems",
          "Module 2: Partial Derivatives & Maxima-Minima of Two Variables",
          "Module 3: First-Order and Higher-Order ODEs with Constant Coefficients",
          "Module 4: Matrices, Eigenvalues, Eigenvectors & Cayley-Hamilton Theorem"
        ],
        progress: 95,
        rating: "4.8",
        time: "16 min",
        color: "blue",
        icon: "⌘",
        next: "Cayley-Hamilton Theorem Applications",
        description: "Rigorous single and multi-variable calculus combined with matrix transformations and differential equations.",
        pyqs: [
          {
            id: "MA1001-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Verify Rolle's Theorem for f(x) = x^2 - 4x + 3 in the interval [1, 3].", marks: 5, module: "Calculus" },
              { qNo: 2, text: "Find the eigenvalues and eigenvectors of the matrix A = [[1, 2], [3, 2]].", marks: 10, module: "Matrices" }
            ]
          }
        ]
      },
      {
        code: "PH 1001",
        title: "Physics",
        shortTitle: "Engineering Physics",
        category: "Basic Sciences",
        credits: 4,
        semester: 1,
        topic: "Optics · Quantum Mechanics · Lasers · Oscillations",
        modules: [
          "Module 1: Oscillations & Wave Propagation",
          "Module 2: Wave Optics - Interference & Diffraction (Newton's Rings)",
          "Module 3: Quantum Mechanics - Schrödinger Wave Equation",
          "Module 4: Lasers, Optical Fibres & Nanotechnology"
        ],
        progress: 90,
        rating: "4.7",
        time: "12 min",
        color: "peach",
        icon: "◉",
        next: "Time-Independent Schrödinger Equation",
        description: "Wave optics, quantum foundation, and optoelectronic principles for computing hardware.",
        pyqs: []
      }
    ]
  },
  {
    semester: 2,
    label: "Semester 2",
    stage: "Freshman",
    session: "Spring Session",
    courses: [
      {
        code: "CS 1002",
        title: "Object-Oriented Programming with C++",
        shortTitle: "OOP with C++",
        category: "Core",
        credits: 4,
        semester: 2,
        topic: "Classes · Polymorphism · Templates · STL",
        modules: [
          "Module 1: OOP Paradigms vs Procedural Programming",
          "Module 2: Constructors, Destructors & Copy Semantics",
          "Module 3: Operator Overloading & Friend Functions",
          "Module 4: Inheritance, Virtual Functions & Pure Abstract Classes",
          "Module 5: Templates & Standard Template Library (STL vectors, maps)"
        ],
        progress: 100,
        rating: "4.9",
        time: "15 min",
        color: "lavender",
        icon: "⌘",
        next: "Virtual Table (vptr & vtable) Internals",
        description: "Modern C++ encapsulation, dynamic dispatch, RAII memory idioms, and generic programming.",
        pyqs: [
          {
            id: "CS1002-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Spring",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Explain late binding versus early binding with an inheritance code example using virtual functions.", marks: 10, module: "Polymorphism" },
              { qNo: 2, text: "Overload the '+' operator to concatenate two custom String objects in C++.", marks: 10, module: "Operator Overloading" }
            ]
          }
        ]
      },
      {
        code: "MA 1002",
        title: "Mathematics - II",
        shortTitle: "Vector Calculus & Transforms",
        category: "Basic Sciences",
        credits: 4,
        semester: 2,
        topic: "Vector Calculus · Laplace Transforms · Fourier Series",
        modules: [
          "Module 1: Multiple Integrals (Double and Triple)",
          "Module 2: Vector Calculus (Gradient, Divergence, Curl, Gauss & Stokes Theorems)",
          "Module 3: Laplace Transforms and Inverse Laplace Transforms",
          "Module 4: Fourier Series and Half-Range Expansions"
        ],
        progress: 95,
        rating: "4.8",
        time: "18 min",
        color: "mint",
        icon: "▤",
        next: "Stokes' Theorem in Computational Physics",
        description: "Multivariate integral calculus, integral theorems, Laplace transforms, and frequency decomposition.",
        pyqs: []
      },
      {
        code: "EC 1001",
        title: "Basic Electronics",
        shortTitle: "Basic Electronics",
        category: "Basic Sciences",
        credits: 3,
        semester: 2,
        topic: "Diodes · BJTs · Op-Amps · Digital Logic Gates",
        modules: [
          "Module 1: Semiconductor Diodes & Rectifier Circuits",
          "Module 2: Bipolar Junction Transistors (BJT) Characteristics",
          "Module 3: Operational Amplifiers (Inverting, Non-Inverting, Summing)",
          "Module 4: Boolean Algebra & Basic Digital Gates"
        ],
        progress: 90,
        rating: "4.6",
        time: "13 min",
        color: "peach",
        icon: "◉",
        next: "Op-Amp Comparators and Slew Rate",
        description: "Solid-state electronic circuits, transistor amplification, operational amplifiers, and digital logic gates.",
        pyqs: []
      }
    ]
  },
  {
    semester: 3,
    label: "Semester 3",
    stage: "Sophomore",
    session: "Autumn Session",
    courses: [
      {
        code: "CS 2001",
        title: "Data Structures and Algorithms",
        shortTitle: "DSA",
        category: "Core",
        credits: 4,
        semester: 3,
        topic: "Trees · Heaps · BST · AVL · Graphs · Hashing",
        modules: [
          "Module 1: Time & Space Complexity (Big-O, Omega, Theta)",
          "Module 2: Singly, Doubly, Circular Linked Lists, Stacks & Queues",
          "Module 3: Trees, Binary Search Trees & Self-Balancing AVL Trees",
          "Module 4: Min/Max Heaps & Priority Queues",
          "Module 5: Graph Representations, BFS, DFS & Topological Sort",
          "Module 6: Collision Resolution Techniques in Hash Tables"
        ],
        progress: 88,
        rating: "5.0",
        time: "20 min",
        color: "mint",
        icon: "▤",
        next: "AVL Tree Rotations (LL, RR, LR, RL)",
        description: "Essential data abstractions, asymptotic analysis, hierarchical trees, and graph traversal algorithms.",
        pyqs: [
          {
            id: "CS2001-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Construct an AVL tree by inserting the elements: 50, 20, 60, 10, 8, 15, 30. Show all rotations.", marks: 10, module: "AVL Trees" },
              { qNo: 2, text: "Implement a circular queue using an array. Write enqueue() and dequeue() methods with boundary checks.", marks: 10, module: "Queues" },
              { qNo: 3, text: "Explain time complexity of building a heap from an unsorted array of size N. Prove it is O(N).", marks: 10, module: "Heaps" }
            ]
          },
          {
            id: "CS2001-END-2024",
            examType: "End-Semester",
            year: 2024,
            session: "Autumn",
            duration: "3 Hours",
            totalMarks: 100,
            questions: [
              { qNo: 1, text: "Explain Dijkstra's shortest path algorithm. Trace for a given weighted directed graph of 6 vertices.", marks: 15, module: "Graphs" },
              { qNo: 2, text: "Differentiate between separate chaining and open addressing (linear probing, quadratic probing, double hashing).", marks: 15, module: "Hashing" }
            ]
          }
        ]
      },
      {
        code: "CS 2003",
        title: "Computer Organization & Architecture",
        shortTitle: "COA",
        category: "Core",
        credits: 4,
        semester: 3,
        topic: "Pipelining · Cache Mapping · Booth's Multiplier · Addressing",
        modules: [
          "Module 1: Register Transfer Language & Micro-operations",
          "Module 2: Instruction Formats & Addressing Modes",
          "Module 3: Computer Arithmetic (Booth's Algorithm, Restoring/Non-Restoring Division)",
          "Module 4: Pipelining: Data Hazards, Control Hazards & Branch Prediction",
          "Module 5: Memory Hierarchy: Direct, Associative & Set-Associative Cache"
        ],
        progress: 82,
        rating: "4.8",
        time: "16 min",
        color: "peach",
        icon: "◉",
        next: "Cache Miss Calculations & Hit Ratio",
        description: "CPU micro-architecture, instruction pipelines, arithmetic circuits, and memory subsystem hierarchy.",
        pyqs: [
          {
            id: "CS2003-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Multiply (+7) by (-5) using Booth's Multiplication Algorithm in 5-bit 2's complement representation.", marks: 10, module: "Computer Arithmetic" },
              { qNo: 2, text: "A 4-way set associative cache memory has 128 cache lines. Main memory size is 64 KB and line size is 16 bytes. Find tag, set, and word offset bits.", marks: 10, module: "Memory Hierarchy" }
            ]
          }
        ]
      },
      {
        code: "MA 2001",
        title: "Discrete Mathematics",
        shortTitle: "Discrete Math",
        category: "Basic Sciences",
        credits: 4,
        semester: 3,
        topic: "Logic · Recurrence · Relations · Graph Theory",
        modules: [
          "Module 1: Propositional Logic, Truth Tables & Normal Forms (CNF/DNF)",
          "Module 2: Set Theory, Relations, Equivalence Classes & POSETs",
          "Module 3: Recurrence Relations and Generating Functions",
          "Module 4: Graph Theory: Euler Paths, Hamiltonian Circuits & Planar Graphs"
        ],
        progress: 85,
        rating: "4.7",
        time: "15 min",
        color: "lavender",
        icon: "⌘",
        next: "Solving Recurrence Relations using Generating Functions",
        description: "Mathematical foundations of computer science: proof strategies, combinatorics, relations, and graph structures.",
        pyqs: []
      }
    ]
  },
  {
    semester: 4,
    label: "Semester 4",
    stage: "Sophomore",
    session: "Spring Session",
    courses: [
      {
        code: "CS 2002",
        title: "Operating Systems",
        shortTitle: "Operating Systems",
        category: "Core",
        credits: 4,
        semester: 4,
        topic: "Semaphores · Deadlocks · Scheduling · Virtual Memory",
        modules: [
          "Module 1: OS Services, System Calls & Dual-Mode Execution",
          "Module 2: Process Scheduling (FCFS, SJF, SRTF, Round Robin, Multi-level Queue)",
          "Module 3: Process Synchronization (Critical Section, Semaphores, Monitors, Dining Philosophers)",
          "Module 4: Deadlocks: Characterization, Prevention, Avoidance (Banker's Algorithm), Detection",
          "Module 5: Memory Management: Paging, Segmentation, Page Replacement (FIFO, LRU, Optimal)",
          "Module 6: File System Implementation, Inodes & Disk Scheduling (SCAN, C-SCAN)"
        ],
        progress: 80,
        rating: "4.9",
        time: "12 min",
        color: "peach",
        icon: "◉",
        next: "Banker's Algorithm for Deadlock Avoidance",
        description: "Process lifecycle, synchronization primitives, memory virtualization, demand paging, and storage management.",
        pyqs: [
          {
            id: "CS2002-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Spring",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Consider 5 processes P0 through P4 with given Allocation, Max, and Available matrices. Determine if the system is in a safe state using Banker's Algorithm.", marks: 12, module: "Deadlocks" },
              { qNo: 2, text: "Explain the Reader-Writer problem and write semaphore-based code providing writer priority.", marks: 10, module: "Synchronization" },
              { qNo: 3, text: "Compare Round Robin scheduling with Multi-Level Feedback Queue scheduling.", marks: 8, module: "CPU Scheduling" }
            ]
          },
          {
            id: "CS2002-END-2024",
            examType: "End-Semester",
            year: 2024,
            session: "Spring",
            duration: "3 Hours",
            totalMarks: 100,
            questions: [
              { qNo: 1, text: "A system uses demand paging. Given reference string: 7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1 with 3 frames. Compute page faults for FIFO, LRU, and Optimal replacement.", marks: 16, module: "Memory Management" },
              { qNo: 2, text: "Explain inode structure in UNIX. Calculate max file size supported given direct, single, double, and triple indirect pointers.", marks: 14, module: "File Systems" }
            ]
          }
        ]
      },
      {
        code: "CS 2004",
        title: "Design & Analysis of Algorithms",
        shortTitle: "DAA",
        category: "Core",
        credits: 4,
        semester: 4,
        topic: "Divide & Conquer · Greedy · DP · NP-Completeness",
        modules: [
          "Module 1: Asymptotic Notations & Master Theorem for Recurrences",
          "Module 2: Divide & Conquer (Merge Sort, Quick Sort, Strassen's Matrix Multiplication)",
          "Module 3: Greedy Method (Huffman Coding, Fractional Knapsack, Prim's & Kruskal's)",
          "Module 4: Dynamic Programming (0/1 Knapsack, Longest Common Subsequence, Matrix Chain)",
          "Module 5: Backtracking (N-Queens, Graph Coloring) & Branch-and-Bound",
          "Module 6: Complexity Classes: P, NP, NP-Hard, NP-Complete (Cook's Theorem)"
        ],
        progress: 75,
        rating: "5.0",
        time: "18 min",
        color: "lavender",
        icon: "⌘",
        next: "Matrix Chain Multiplication DP recurrence",
        description: "Algorithmic strategies, optimality proofs, dynamic programming memoization, and computational complexity limits.",
        pyqs: [
          {
            id: "CS2004-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Spring",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Solve recurrence T(n) = 3T(n/2) + n^2 using Master's Theorem.", marks: 6, module: "Recurrences" },
              { qNo: 2, text: "Find the Longest Common Subsequence between X = 'BACDB' and Y = 'BDCB' using Dynamic Programming. Show the c[i,j] and b[i,j] tables.", marks: 14, module: "Dynamic Programming" },
              { qNo: 3, text: "Construct Huffman tree and determine binary codes for characters with frequencies: a:45, b:13, c:12, d:16, e:9, f:5.", marks: 10, module: "Greedy" }
            ]
          }
        ]
      },
      {
        code: "CS 2006",
        title: "Database Management Systems",
        shortTitle: "DBMS",
        category: "Core",
        credits: 4,
        semester: 4,
        topic: "ACID · Normalization · 2PL · Relational Algebra",
        modules: [
          "Module 1: ER Modeling, Conceptual Design & Relational Model Mapping",
          "Module 2: Relational Algebra & Advanced SQL Queries",
          "Module 3: Normalization Theory (Functional Dependencies, 1NF, 2NF, 3NF, BCNF)",
          "Module 4: Transaction Processing & ACID Properties",
          "Module 5: Concurrency Control (Two-Phase Locking 2PL, Timestamp Ordering)",
          "Module 6: Database Recovery (WAL, Checkpoints, ARIES)"
        ],
        progress: 65,
        rating: "4.9",
        time: "15 min",
        color: "mint",
        icon: "▤",
        next: "Two-Phase Locking (2PL) Protocols",
        description: "Relational data structures, schema normalization, transaction isolation levels, and ACID persistence engines.",
        pyqs: [
          {
            id: "CS2006-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Spring",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Given relation R(A, B, C, D, E) with FDs {A->BC, CD->E, B->D, E->A}. Find candidate keys and highest normal form.", marks: 12, module: "Normalization" },
              { qNo: 2, text: "Explain Conflict Serializability. Test if schedule S: r1(A); w2(A); r1(B); w2(B); r3(B); w3(B) is conflict serializable using precedence graph.", marks: 10, module: "Transactions" },
              { qNo: 3, text: "Differentiate between Strict 2PL and Rigorous 2PL.", marks: 8, module: "Concurrency Control" }
            ]
          }
        ]
      }
    ]
  },
  {
    semester: 5,
    label: "Semester 5",
    stage: "Junior",
    session: "Autumn Session",
    courses: [
      {
        code: "CS 3001",
        title: "Computer Networks",
        shortTitle: "Computer Networks",
        category: "Core",
        credits: 4,
        semester: 5,
        topic: "OSI/TCP · Subnetting · BGP · TCP Congestion Control",
        modules: [
          "Module 1: Layered Architectures (OSI 7 Layers vs TCP/IP Suite)",
          "Module 2: Data Link Layer: Framing, Flow Control (Go-Back-N, Selective Repeat)",
          "Module 3: Network Layer: IPv4/IPv6 Addressing, Subnetting, CIDR",
          "Module 4: Routing Protocols: Distance Vector (Bellman-Ford), Link State (Dijkstra), OSPF, BGP",
          "Module 5: Transport Layer: TCP 3-Way Handshake, Flow Control & AIMD Congestion Control",
          "Module 6: Application Layer: DNS, HTTP/2, SMTP, DHCP"
        ],
        progress: 70,
        rating: "4.9",
        time: "16 min",
        color: "blue",
        icon: "⌘",
        next: "TCP AIMD Slow Start and Congestion Avoidance",
        description: "Packet switched networking, IP address subnetting, intra/inter-domain routing, and transport flow control.",
        pyqs: [
          {
            id: "CS3001-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "An ISP is granted a block of addresses starting with 192.168.16.0/24. Distribute to 3 organizations requiring 60, 30, and 12 hosts. Give address ranges and subnet masks.", marks: 12, module: "Network Layer" },
              { qNo: 2, text: "Explain count-to-infinity problem in Distance Vector routing. How does Split Horizon with Poison Reverse mitigate it?", marks: 10, module: "Routing" },
              { qNo: 3, text: "Calculate channel efficiency for Go-Back-N with window size N = 7, bandwidth 1 Mbps, propagation delay 250 ms, frame size 1000 bits.", marks: 8, module: "Data Link Layer" }
            ]
          }
        ]
      },
      {
        code: "CS 3003",
        title: "Software Engineering",
        shortTitle: "Software Eng",
        category: "Core",
        credits: 4,
        semester: 5,
        topic: "Agile · Scrum · UML Design · CI/CD · Testing",
        modules: [
          "Module 1: Software Lifecycle Models (Waterfall, Spiral, Agile/Scrum)",
          "Module 2: Requirements Engineering & Software Requirement Specification (SRS)",
          "Module 3: OOAD & UML Diagrams (Use Case, Class, Sequence, Activity)",
          "Module 4: Software Metrics & COCOMO Cost Estimation",
          "Module 5: Software Testing: Black-Box (Equivalence, BVA) & White-Box (Cyclomatic Complexity)",
          "Module 6: DevOps, Continuous Integration / Continuous Deployment (CI/CD)"
        ],
        progress: 78,
        rating: "4.8",
        time: "14 min",
        color: "mint",
        icon: "▤",
        next: "Cyclomatic Complexity Calculation from Control Flow Graph",
        description: "Software specification, iterative agile processes, UML structural modeling, and automated test verification.",
        pyqs: []
      },
      {
        code: "CS 3007",
        title: "Compiler Design",
        shortTitle: "Compiler Design",
        category: "Core",
        credits: 4,
        semester: 5,
        topic: "Lexical Analysis · LL(1) / LR Parsing · TAC · Code Gen",
        modules: [
          "Module 1: Phases of a Compiler and Front-End / Back-End Separation",
          "Module 2: Lexical Analysis & Finite Automata Implementation",
          "Module 3: Syntax Analysis: Top-Down (LL(1)) & Bottom-Up (SLR, CLR, LALR)",
          "Module 4: Syntax-Directed Translation & Type Checking",
          "Module 5: Intermediate Code Generation (Three-Address Code, Quadruples, Triples)",
          "Module 6: Code Optimization & Target Machine Code Generation"
        ],
        progress: 60,
        rating: "4.7",
        time: "17 min",
        color: "peach",
        icon: "◉",
        next: "Computing FIRST and FOLLOW sets for LL(1) Parsing Table",
        description: "Grammar analysis, context-free parsing algorithms, syntax-directed translation, and compiler optimization pipelines.",
        pyqs: []
      }
    ]
  },
  {
    semester: 6,
    label: "Semester 6",
    stage: "Junior",
    session: "Spring Session",
    courses: [
      {
        code: "CS 3002",
        title: "Machine Learning",
        shortTitle: "Machine Learning",
        category: "Core",
        credits: 4,
        semester: 6,
        topic: "Supervised · SVM · Random Forests · Neural Nets",
        modules: [
          "Module 1: Learning Foundations, Bias-Variance Tradeoff & Evaluation Metrics",
          "Module 2: Linear & Logistic Regression with Gradient Descent Optimization",
          "Module 3: Decision Trees (ID3, C4.5), Random Forests & Ensemble Boosting",
          "Module 4: Support Vector Machines (SVM), Hyperplane Geometry & Kernel Trick",
          "Module 5: Unsupervised Learning: K-Means Clustering & PCA Dimensionality Reduction",
          "Module 6: Multilayer Perceptron & Backpropagation Algorithm"
        ],
        progress: 85,
        rating: "5.0",
        time: "18 min",
        color: "lavender",
        icon: "⌘",
        next: "Backpropagation Mathematical Derivation",
        description: "Mathematical formulation of statistical machine learning algorithms, model evaluation, and kernelized classification.",
        pyqs: [
          {
            id: "CS3002-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Spring",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Derive gradient descent weight update rule for linear regression with Mean Squared Error loss.", marks: 10, module: "Supervised Learning" },
              { qNo: 2, text: "Explain maximum margin hyperplane in SVM. How do soft margins and slack variables handle non-separable data?", marks: 12, module: "SVM" },
              { qNo: 3, text: "Calculate information gain and Gini impurity for a given binary attribute split.", marks: 8, module: "Decision Trees" }
            ]
          }
        ]
      },
      {
        code: "CS 3004",
        title: "Cloud Computing",
        shortTitle: "Cloud Computing",
        category: "Core",
        credits: 3,
        semester: 6,
        topic: "Virtualization · IaaS/PaaS/SaaS · Docker · Kubernetes",
        modules: [
          "Module 1: Cloud Service Models (IaaS, PaaS, SaaS) & Deployment Architectures",
          "Module 2: Hypervisors, Hardware Emulation & Operating System Virtualization",
          "Module 3: Containerization: Docker Container Engine, Images & Dockerfiles",
          "Module 4: Container Orchestration: Kubernetes Pods, Deployments & Services",
          "Module 5: Cloud Storage & Distributed Databases (DynamoDB, S3, Cassandra)"
        ],
        progress: 72,
        rating: "4.8",
        time: "15 min",
        color: "blue",
        icon: "⌘",
        next: "Kubernetes Ingress Controllers and Service Discovery",
        description: "Cloud elasticity, multi-tenancy, virtualization mechanisms, container orchestration, and serverless architectures.",
        pyqs: []
      },
      {
        code: "CS 3006",
        title: "Cryptography & Network Security",
        shortTitle: "Cryptography",
        category: "Core",
        credits: 4,
        semester: 6,
        topic: "AES · RSA · Diffie-Hellman · SHA-256 · SSL/TLS",
        modules: [
          "Module 1: Classical Ciphers & Cryptanalysis (Substitution, Transposition)",
          "Module 2: Symmetric Block Ciphers: Data Encryption Standard (DES) & AES",
          "Module 3: Asymmetric Ciphers: RSA Algorithm & Miller-Rabin Primality Test",
          "Module 4: Key Exchange Protocols: Diffie-Hellman & Man-In-The-Middle Prevention",
          "Module 5: Cryptographic Hash Functions (SHA-256) & HMAC",
          "Module 6: Digital Signatures, PKI, X.509 Certificates & SSL/TLS Handshake"
        ],
        progress: 68,
        rating: "4.9",
        time: "15 min",
        color: "peach",
        icon: "◉",
        next: "RSA Key Generation and Encryption/Decryption Steps",
        description: "Mathematical cryptography, symmetric and asymmetric ciphers, public key infrastructure, and authenticated key exchange.",
        pyqs: []
      }
    ]
  },
  {
    semester: 7,
    label: "Semester 7",
    stage: "Senior",
    session: "Fall 2026",
    isCurrent: true,
    courses: [
      {
        code: "CS 4001",
        title: "Distributed Systems",
        shortTitle: "Distributed Systems",
        category: "Core",
        credits: 4,
        semester: 7,
        topic: "RPC · Lamport Clocks · Paxos/Raft · GFS/HDFS",
        modules: [
          "Module 1: Characterization of Distributed Systems & CAP Theorem",
          "Module 2: Inter-process Communication: Remote Procedure Call (RPC) & RMI",
          "Module 3: Logical Clocks: Lamport Timestamps & Vector Clocks",
          "Module 4: Mutual Exclusion & Distributed Leader Election (Bully & Ring Algorithms)",
          "Module 5: Distributed Consensus: Two-Phase Commit (2PC), Paxos & Raft",
          "Module 6: Distributed File Systems: Google File System (GFS) & HDFS Replication"
        ],
        progress: 85,
        rating: "5.0",
        time: "18 min",
        color: "mint",
        icon: "▤",
        next: "Raft Consensus Algorithm Leader Election & Log Replication",
        description: "Architectural models, distributed logical time, consensus protocols, distributed locks, and fault tolerance.",
        pyqs: [
          {
            id: "CS4001-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Explain Lamport's logical clocks. In a distributed system with 3 processes P1, P2, P3, trace event timestamps following message passing rules.", marks: 10, module: "Time & Clocks" },
              { qNo: 2, text: "State and prove the CAP Theorem. How do modern distributed databases (e.g. Cassandra vs MongoDB) make trade-offs between CP and AP?", marks: 10, module: "Architectures" },
              { qNo: 3, text: "Compare the Bully Election Algorithm with the Ring Election Algorithm in terms of message complexity.", marks: 10, module: "Leader Election" }
            ]
          },
          {
            id: "CS4001-END-2024",
            examType: "End-Semester",
            year: 2024,
            session: "Autumn",
            duration: "3 Hours",
            totalMarks: 100,
            questions: [
              { qNo: 1, text: "Explain the Raft consensus protocol. Detail the Leader Election, Log Replication, and Safety invariants.", marks: 20, module: "Consensus" },
              { qNo: 2, text: "Describe Google File System (GFS) architecture. Explain how chunk servers, master node, and 64MB chunk sizes handle large streaming reads and concurrent record appends.", marks: 18, module: "Distributed File Systems" },
              { qNo: 3, text: "Describe Two-Phase Commit (2PC) protocol. What happens if the coordinator crashes during the Prepare phase or Commit phase?", marks: 16, module: "Transactions" }
            ]
          }
        ]
      },
      {
        code: "CS 4003",
        title: "Deep Learning & Neural Networks",
        shortTitle: "Deep Learning",
        category: "Core",
        credits: 4,
        semester: 7,
        topic: "CNN · ResNet · Transformers · Attention · GANs",
        modules: [
          "Module 1: Deep Feedforward Networks, Loss Functions & Regularization (Dropout, Batch Norm)",
          "Module 2: Convolutional Neural Networks (CNN): Convolution, Pooling, ResNet Skip Connections",
          "Module 3: Recurrent Neural Networks (RNN), Vanishing Gradients, LSTM & GRU Cells",
          "Module 4: Sequence-to-Sequence Models & Scaled Dot-Product Self-Attention",
          "Module 5: Transformer Architecture (Multi-Head Attention, Positional Encoding, BERT & GPT)",
          "Module 6: Generative Adversarial Networks (GANs) & Diffusion Models"
        ],
        progress: 80,
        rating: "4.9",
        time: "22 min",
        color: "lavender",
        icon: "⌘",
        next: "Transformer Self-Attention Matrix Calculation Q*K^T / sqrt(d_k)",
        description: "Modern deep neural architectures, residual vision models, sequence modeling, self-attention, and generative models.",
        pyqs: [
          {
            id: "CS4003-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Given an input image of dimension 32x32x3, apply 16 filters of size 5x5 with stride 1 and padding 2. Compute the output feature map dimension and total trainable parameters.", marks: 10, module: "CNN" },
              { qNo: 2, text: "Explain why standard RNNs suffer from vanishing and exploding gradients. How do LSTM forget, input, and output gates resolve this?", marks: 10, module: "RNN & LSTM" },
              { qNo: 3, text: "Explain how Batch Normalization accelerates deep network training and reduces internal covariate shift.", marks: 10, module: "Optimization" }
            ]
          },
          {
            id: "CS4003-END-2024",
            examType: "End-Semester",
            year: 2024,
            session: "Autumn",
            duration: "3 Hours",
            totalMarks: 100,
            questions: [
              { qNo: 1, text: "Detail the Transformer architecture. Derive the Scaled Dot-Product Attention equation and explain why dividing by sqrt(d_k) prevents softmax saturation.", marks: 20, module: "Transformers" },
              { qNo: 2, text: "Explain the minimax objective function of Generative Adversarial Networks (GANs). Discuss Mode Collapse and how Wasserstein GAN (WGAN) addresses it.", marks: 18, module: "Generative Models" }
            ]
          }
        ]
      },
      {
        code: "CS 4005",
        title: "Big Data Analytics & Data Warehousing",
        shortTitle: "Big Data",
        category: "Core",
        credits: 3,
        semester: 7,
        topic: "Hadoop · MapReduce · Spark RDDs · Star Schema",
        modules: [
          "Module 1: The 5 V's of Big Data & Distributed Storage Architecture",
          "Module 2: Hadoop MapReduce: Map, Shuffle, Sort, Reduce Paradigm",
          "Module 3: Apache Spark: Resilient Distributed Datasets (RDDs), Transformations & Actions",
          "Module 4: Data Warehousing: Star Schema, Snowflake Schema & Fact Constellations",
          "Module 5: OLAP Operations: Roll-up, Drill-down, Slice, Dice & Pivot",
          "Module 6: Association Rule Mining (Apriori Algorithm) & Frequent Itemsets"
        ],
        progress: 72,
        rating: "4.8",
        time: "15 min",
        color: "blue",
        icon: "◉",
        next: "Apache Spark RDD Lineage Graph and Lazy Evaluation",
        description: "Massive scale parallel computation, in-memory DAG pipelines with Spark, multidimensional modeling, and OLAP cubes.",
        pyqs: [
          {
            id: "CS4005-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Write MapReduce pseudo-code for Word Count. Trace the mapper outputs, shuffle/sort phase, and reducer aggregation.", marks: 12, module: "MapReduce" },
              { qNo: 2, text: "Design a Star Schema for a university examination management system including Fact table and Dimension tables.", marks: 10, module: "Data Warehousing" },
              { qNo: 3, text: "Differentiate between Narrow Transformations and Wide Transformations in Apache Spark with examples.", marks: 8, module: "Apache Spark" }
            ]
          }
        ]
      },
      {
        code: "CS 4007",
        title: "Internet of Things (IoT) & Embedded Systems",
        shortTitle: "IoT & Embedded",
        category: "Elective",
        credits: 3,
        semester: 7,
        topic: "MQTT · CoAP · ESP32 · Edge Computing · Sensors",
        modules: [
          "Module 1: IoT Reference Architecture & Sensing Subsystems",
          "Module 2: Microcontroller Platforms: ESP32, Arduino, Raspberry Pi",
          "Module 3: Communication Protocols: MQTT (Publish/Subscribe), CoAP (RESTful IoT), Zigbee",
          "Module 4: Edge Computing & Low-Power Wide-Area Networks (LoRaWAN)",
          "Module 5: Security Challenges in Connected Devices & Firmware Hardening"
        ],
        progress: 65,
        rating: "4.7",
        time: "14 min",
        color: "peach",
        icon: "⌘",
        next: "MQTT QoS Levels (0, 1, 2) Packet Flow Analysis",
        description: "Sensor networks, publish-subscribe telemetry, edge device programming, and wireless IoT protocols.",
        pyqs: [
          {
            id: "CS4007-MID-2024",
            examType: "Mid-Semester",
            year: 2024,
            session: "Autumn",
            duration: "1.5 Hours",
            totalMarks: 30,
            questions: [
              { qNo: 1, text: "Explain MQTT protocol architecture and compare QoS Level 0, Level 1, and Level 2 message flows with packet handshake diagrams.", marks: 12, module: "Protocols" },
              { qNo: 2, text: "Differentiate between Cloud Computing and Edge Computing in IoT architectures with latency and bandwidth considerations.", marks: 10, module: "Edge Computing" }
            ]
          }
        ]
      },
      {
        code: "CS 4091",
        title: "Major Project (Phase - I)",
        shortTitle: "Major Project I",
        category: "Project",
        credits: 4,
        semester: 7,
        topic: "Literature Review · Architecture · SRS · Multi-Agent GenAI",
        modules: [
          "Module 1: Problem Identification & Domain Research",
          "Module 2: Comprehensive Literature Survey & Scopus/IEEE Benchmark Papers",
          "Module 3: Software Requirement Specification (SRS) & System Architecture Design",
          "Module 4: Prototype Development & Multi-Agent Integration",
          "Module 5: Mid-term Progress Review, Viva Voce & Evaluation Committee Defense"
        ],
        progress: 90,
        rating: "5.0",
        time: "30 min",
        color: "mint",
        icon: "★",
        next: "System Demonstration & Multi-Agent Collaboration Viva",
        description: "Design and implement the initial architectural foundation for StudySync: 6 collaborative GenAI agents.",
        pyqs: []
      }
    ]
  },
  {
    semester: 8,
    label: "Semester 8",
    stage: "Senior",
    session: "Spring 2027",
    courses: [
      {
        code: "CS 4092",
        title: "Major Project (Phase - II) / Capstone Project",
        shortTitle: "Major Project II",
        category: "Project",
        credits: 10,
        semester: 8,
        topic: "Final Deployment · Research Paper · Scopus/IEEE Publication",
        modules: [
          "Module 1: End-to-End System Implementation & Agent Pipeline Tuning",
          "Module 2: Rigorous Empirical Verification & Latency Benchmarks",
          "Module 3: Research Paper Drafting for IEEE / Springer / Scopus Conference",
          "Module 4: Final Capstone Defense & External Examiner Viva Voce"
        ],
        progress: 10,
        rating: "5.0",
        time: "40 min",
        color: "mint",
        icon: "★",
        next: "Full-Stack Deployment & Thesis Submission",
        description: "Capstone research, full deployment, empirical evaluation, and external university dissertation defense.",
        pyqs: []
      },
      {
        code: "CS 4002",
        title: "Research Ethics, IPR & Patent Law",
        shortTitle: "IPR & Ethics",
        category: "Core",
        credits: 3,
        semester: 8,
        topic: "Patent Claims · Copyright · Research Integrity · Plagiarism",
        modules: [
          "Module 1: Philosophy of Research & Plagiarism Guidelines (UGC/AICTE)",
          "Module 2: Intellectual Property Rights (IPR): Patents, Trademarks, Copyrights",
          "Module 3: Patent Drafting: Claims, Prior Art Search & Indian Patent Office Filing",
          "Module 4: Cyber Law, IT Act 2000 & Software Licensing (GPL, MIT, Apache)"
        ],
        progress: 5,
        rating: "4.8",
        time: "15 min",
        color: "lavender",
        icon: "▤",
        next: "Patent Prior Art Search and Claim Structuring",
        description: "Legal protection of software innovations, patent drafting methodology, and research academic integrity.",
        pyqs: []
      }
    ]
  }
]

export function getSemesterData(semesterNum: number): SemesterData {
  return KIIT_CURRICULUM.find(s => s.semester === semesterNum) || KIIT_CURRICULUM[6] // default Sem 7
}

export function getAllSemesters(): { semester: number; label: string; stage: string; isCurrent?: boolean }[] {
  return KIIT_CURRICULUM.map(s => ({
    semester: s.semester,
    label: s.label,
    stage: s.stage,
    isCurrent: s.isCurrent
  }))
}

export function getAllPYQCount(): number {
  return KIIT_CURRICULUM.reduce((sum, sem) => {
    return sum + sem.courses.reduce((cSum, course) => cSum + course.pyqs.length, 0)
  }, 0)
}
