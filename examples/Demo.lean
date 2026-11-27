-- Tiny smoke-test declaration; not an open problem or a benchmark.
-- Copy into a trusted Lake project's library module, e.g. MyProject/Proof.lean.
namespace ConjectureDemo

theorem add_comm (a b : Nat) : a + b = b + a := by
  exact Nat.add_comm a b

end ConjectureDemo
