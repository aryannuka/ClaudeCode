# Competition Proof Style

Write competition math proofs the way a talented undergraduate sophomore (strong AIME/Olympiad background) would — direct, minimal, no AI-typical magic leaps.

## Core Principles

**Find the simplest structural observation first.**
If a sequence of positive integers strictly decreases, that one sentence is the proof — don't build product telescopes or divisibility chains around it.

**Use standard tools before inventing machinery.**
- Taylor series / alternating series bound → before derivative sign analysis
- AM-GM, Cauchy-Schwarz → before constructing auxiliary functions
- Direct involution / pairing → before Hamiltonian paths or matching theory

**Never build infrastructure when a single quantity witnesses the bound.**
One decreasing positive integer sequence, one Taylor inequality, one explicit bijection.

**Be concise.** Math over words. No "we note that", no "it is easy to see", no paragraph-long motivation before the actual step.

## Specific Patterns

### Sequences / Divisibility
Track the odd part of a difference (or similar single quantity):
- If `gcd(aₖ, bₖ) > 1` forces `bₖ₊₁ < bₖ` and `bₖ ≥ 1`, then `gcd > 1` happens finitely often. Done.
- Don't track the product `d₀·d₁·…·dₖ` dividing some fixed constant — it's the same argument, worse notation.

### Inequalities on [0, π]
For `f(x) ≥ 0` with `f(0) = f(π) = 0`:
1. **Lower bound**: Try `sin x ≥ x − x³/6` (Taylor, alternating series) before second-derivative analysis.
   - Check `sin x − x(π−x)/π ≥ x²(1/π − x/6)` and verify the coefficient is positive.
2. **Upper bound** (`h ≥ 0` on `[0, π/2]` with `h(0) = h(π/2) = 0`, `h′(0) > 0`):
   - Count zeros of `h″` in `(0, π/2)`. If exactly one → `h′` is unimodal (decreasing then increasing) → `h′` has at most one sign change (+ to −) in `(0, π/2)` by Rolle → `h` rises then falls → minimum at endpoints = 0. Done.

### Game Theory (last-player-loses / combinatorial games)
Look for a **direct involution** on all non-start positions:
- Pair each non-start state `s` with a partner `s′` reachable in one move from `s`.
- Show the pairing is an involution and `s′` is always unvisited when `s` is first reached.
- Invariant: before each of Alice's turns, every pair is both-visited or both-unvisited.
- Bob always mirrors Alice's move to the pair partner → Bob always has a reply → Alice runs out first.

Don't construct Hamiltonian paths, explicit matchings, or inductive position analyses unless the direct pairing genuinely fails.

## What to Avoid

| Avoid | Use instead |
|---|---|
| "Product of gcds divides D₀" | "Odd part of difference strictly decreases" |
| Second-derivative sign chart for lower bound | Taylor series bound in two lines |
| Hamiltonian path / matching for second-player wins | Direct involution on non-start states |
| Roundabout auxiliary functions | The most natural quantity that tracks the obstruction |
| Long English motivation before the math | State the key quantity, then prove it has the claimed property |

## Tone and Format

- State the key quantity or construction up front ("Track bₖ = odd part of |mₖ − nₖ|").
- Give the recurrence / inequality / invariant in one displayed line.
- One short paragraph per logical step. End with ∎.
- No headers unless the proof has genuinely separate parts (lower bound / upper bound).

## Example Structure (A1-style)

```
Track bₖ = odd part of |mₖ − nₖ|.

Key recurrence: |mₖ − nₖ| = 2|m_{k−1} − n_{k−1}| / d_{k−1},
so bₖ = b_{k−1} / d_{k−1}.

Whenever d_{k−1} > 1, we get bₖ < b_{k−1}.
Since bₖ is a positive integer for all k, it can only strictly decrease finitely many times.
Hence d_{k−1} > 1 for only finitely many k. ∎
```
