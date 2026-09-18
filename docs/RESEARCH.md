# Research program

The kernel above is the honest small piece. A full native-to-legacy-to-quantum
transport across AI, robotics, physics, biology, medicine, enterprise, defense,
sensor fusion, and digital twins would require additional layers:

1. Execution substrates. Classical von Neumann, legacy batch/mainframe, and
   quantum gate-model or annealer each have distinct observable algebras and
   error models. Unifying their observation is open.

2. Shared dimensions. SI, ISO 80000, and BIPM cover measurement units but not
   semantic identity. Cross-domain reasoning needs a shared dimensional and
   invariant layer that does not yet exist at the level needed.

3. Preservation semantics. A mapping between two domains can declare what it
   preserves. Proving that the declaration holds for a class of inputs is a
   refinement-typing problem.

4. Composition. Mappings must compose associatively. Whether a given chain of
   domain adapters is well-typed depends on whether the preserved subsets
   intersect.

5. Verification. Every axiom in the kernel has an independence test. Any
   extension must preserve independence. That is MP3.

None of these is solved by naming. All are tractable as multi-year research.

The kernel does not claim any of them are solved. It gives a substrate on
which they can be pursued without redesigning the core.
