# CLAUDE.md

## Solving Conceptual / Competition Math Problems

When asked to solve or prove a math problem, follow these principles.

### Approach

1. **Find the key quantity first.** Before writing anything, identify the one object (a sequence, a ratio, a pairing, a function value) whose behavior directly witnesses the answer. Everything else follows from it.

2. **Prefer elementary over machinery.** In order:
   - Arithmetic / direct computation
   - Taylor series / standard inequalities (AM-GM, Cauchy-Schwarz, alternating series)
   - Counting / combinatorial bijection
   - Calculus (derivatives, Rolle, MVT)
   - Abstract algebra / generating functions / heavier tools
   Only reach for the next tier if the previous one genuinely fails.

3. **No reverse-engineering.** Do not start from the answer and work backwards. Derive it from the structure of the problem.

4. **No magic leaps.** Every step should be something a strong sophomore (AIME/early Olympiad background) could have found by looking at the problem for 10–20 minutes.

### Writing the Proof

- State the key quantity or construction in the first sentence.
- One displayed line for the main recurrence / inequality / invariant.
- One short paragraph per logical step.
- End with ∎.
- No lengthy English motivation before the math. No "we note that", "it is easy to see", "one can verify".
- Headers only when the proof has genuinely separate parts (e.g., lower bound / upper bound).

### Common Patterns

| Problem type | Go-to approach |
|---|---|
| "Something happens finitely often" | Find a positive integer quantity that strictly decreases each time it happens |
| Inequality `f(x) ≥ 0` on `[0,L]`, `f(0)=f(L)=0` | Taylor bound first; if that fails, count zeros of `f″` to control `f′` sign changes |
| Second-player wins game | Find a direct involution pairing all non-start states; invariant: pairs are both-visited or both-unvisited |
| Divisibility / gcd argument | Track the simplest single quantity (odd part, valuation) rather than a product of intermediate gcds |

### What to Avoid

- Building product telescopes or divisibility chains when one decreasing integer suffices.
- Constructing Hamiltonian paths or explicit matchings when a 3-sentence pairing argument works.
- Second-derivative sign charts for a lower bound that follows from two lines of Taylor.
- Multi-paragraph motivation blocks before the actual mathematical content.
- Roundabout auxiliary constructions when the most natural quantity directly solves the problem.

### Style Reference

See `.claude/skills/competition-proof-style.md` for detailed patterns and examples.
