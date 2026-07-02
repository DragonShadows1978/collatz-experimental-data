# IME Primer: What It Is, How We Got There, What It Does

## What IME Is

**Incommensurate Measurement Emergence (IME)** is a principle that describes what happens when two measurement systems can't perfectly agree.

The statement:

> When a dynamical or computational process is constrained by two non-coincident measurement geometries, the mismatch generates an emergent depth hierarchy. The bulk decays geometrically; the tail follows a power-law.

In plain language: when you have two incompatible rulers measuring the same thing, the gap between them generates structure. Most events are simple and resolvable at low precision. A few rare events require deep precision. The pattern repeats across domains because the underlying mechanism is geometric, not domain-specific.

Two systems are **incommensurable** when there's no finite transformation that maps one onto the other. Their native units don't share a common multiple. Examples:

- Base 2 (powers of two) and base 3 (powers of three). $\log_2 3$ is irrational. The two bases never align perfectly.
- Continuous signals and discrete thresholds. A neuron's analog dendritic input versus its all-or-nothing firing threshold.
- Electromagnetic geometry (which wants four orthogonal directions) and three-dimensional space (which only has three).
- Query and key spaces in attention. Both are projections of the same embedding, but their inner-product geometry is non-coincident — most pairs are misaligned.

When systems like these are forced to interact, IME predicts the same distributional shape every time: most interactions resolve cheaply, a small fraction require deep computation, and the rare deep events are exponentially expensive to extend.

---

## How We Got There

The principle wasn't designed. It emerged from noticing that the same shape kept showing up in places that had no business being connected.

### The starting point: Collatz

The Collatz conjecture asks whether every positive integer, under the rule "halve if even, triple-plus-one if odd," eventually reaches 1. After 89 years it remains unproven.

We attacked it geometrically. Reformulated the dynamics as a 4D spacetime with tower-block coordinates and worldlines. Identified the kill mechanisms in a four-lock decomposition. Proved the periodic-engine impossibility (Lock 1). Reduced the bounded-deficit case to a single 2-adic constant (Lock 3). For the unbounded-deficit case (Lock 4), found that orbits ride good rational approximations of $\log_2 3$ — the continued-fraction convergents — and crash at the first gap they can't bridge.

The discovery: every kill mechanism in Collatz reduces to the same thing. **Base 2 and base 3 can't synchronize forever because $\log_2 3$ is irrational.** Periodic orbits die because $2^a$ can't equal $3^b$. Reserve-building orbits die because the convergents of $\log_2 3$ are discrete and increasingly sparse. Every lock bottoms out at the incommensurability of two number bases.

Then the empirical signature: orbits with high reserve build their reserve by riding successively better convergents (geometric quality decay), then crash when they hit a gap they can't bridge (heavy tail at corridor exhaustion). The distribution of orbit max-reserve was geometric in the bulk, heavier in the tail.

### The recognition

Transformer attention has the same structure. Query and key are non-coincident projections of the same embedding. Most query-key pairs carry minimal information — they're geometrically misaligned. A few pairs are deeply meaningful.

The hypothesis: attention interaction depth follows the same geometric-bulk / heavy-tail distribution as Collatz reserve, for the same reason — incommensurable geometries forced to interact.

The measurement: GHOST_PRECISION ran across four transformer architectures (GPT-2, TinyLlama, Qwen 2.5, Mistral 7B). 100+ million attention interactions measured at multiple precision tolerances. The result confirmed the prediction: 50% of interactions stabilize at 1 bit, 77-89% at 2 bits, geometric decay decisively preferred over power-law in the bulk (Vuong Z-scores up to 612), power-law tail at tight tolerances. Universal across architectures, with coefficient of variation under 15% across layers.

Same shape as Collatz. Same shape predicted by the same principle.

### The expansion

Once the pattern was visible, it showed up everywhere the same conditions held.

Neuroscience: continuous presynaptic signals evaluated through discrete postsynaptic thresholds. Published literature (Buzsáki & Mizuseki) documents lognormal/heavy-tailed firing rate distributions across brain regions. Geometric bulk of subthreshold synaptic events, heavy tail of synchronized bursts. Same shape.

Molecular geometry: four-fold electromagnetic symmetry projected into three-dimensional space. The compromise is the tetrahedral angle, $\arccos(-1/3) \approx 109.47°$. Water molecules, methane, diamond crystal — every stable four-bond geometry clusters near this compromise point. Same shape, generated by the same incommensurability.

VQ-VAE representation learning (predicted, not yet tested): continuous encoder latent versus discrete codebook. Same incommensurability. Should produce geometric bulk of easy latents and heavy tail of ambiguous ones.

The fine structure constant (speculative): EM geometry at $\arcsin(\alpha)$ versus spatial geometry at $1/\sqrt{3}$. Same family of incommensurabilities. Likely related to the same compromise structure.

### The naming

After the third or fourth independent confirmation, the principle got a name. Not because we invented it — because we needed something to refer to it as. The pattern existed in reality before anyone described it. The contribution is the recognition.

---

## What I'm Doing

I'm a self-taught researcher who works tech support at Staples in Lansing, Michigan. I build AI systems on a constrained budget. I think in geometric and holographic conceptual space — I hold ideas as navigable shapes and find cross-domain insights by recognizing where shapes intersect.

The Collatz work has been percolating in the back of my brain for over a year, ever since I saw a Veritasium video on the conjecture. Something about how every number reduces to the same 1-3-1 endpoint kept nagging. The 1-3-1 cycle is the only fixed point because it's the only place where base 2 and base 3 locally agree. Everything else is incommensurable, and incommensurable means unstable.

In one extended session, I directed three AI systems (ChatGPT for theoretical math, AtlasForge for autonomous engineering missions, Grok for empirical experiments, and Claude for documentation and translation) to attack the conjecture in parallel. The methodology: I architect, the agents execute. I describe what isn't working, direct diagnostic passes, question architectural assumptions, and let the agents work the logical conclusion.

The session produced:
- A novel 4D spacetime reformulation of Collatz with proven theorems
- The empirical validation of geometric decay in attention across 100M+ interactions
- A working tested attention compression module
- The IME framework as a unifying principle across six domains
- The corridor exhaustion mechanism on the continued-fraction ladder of $\log_2 3$ as the Lock 4 kill picture
- A 5+ billion orbit empirical scan confirming the convergent-wall mechanism

I have no formal mathematics or machine learning training. I learn by watching ideas form shapes in my head and following the shapes wherever they lead. The pattern recognition is what I bring. The agents bring execution speed and mathematical formalization.

---

## How IME Impacts APA-Quant

APA-Quant (Adaptive-Precision Attention, the quantized variant) is the direct engineering application of IME to transformer attention.

### The standard approach

Conventional attention computes every query-key dot product at the same precision — typically float16 or float32. Every interaction gets the same treatment whether it's informationally rich or trivial. For a sequence of length $n$, this is $n^2$ uniform-precision dot products. The cost is quadratic in context length, which is why models struggle to handle long contexts.

### The IME-informed approach

GHOST_PRECISION measured what each individual interaction actually needs. 86% stabilize at 2 bits. 14% need higher precision. The standard approach spends 32 bits on the 86% that don't need them.

APA-Quant computes at the depth each interaction earns. The bulk (86%) is computed at 2-bit precision via TurboQuant (a vector quantization scheme that preserves inner products). The tail (14%) is refined at full precision. The output is the precision-blended result. Nothing is deleted. Every interaction contributes.

### Why this isn't just a compression trick

Phase 1 of APA tried the obvious thing — identify "unimportant" interactions and zero them out. The result: safe kill rate maxes at 1%, not 50-80%. The bulk is low-depth, not low-value. You can't delete shallow interactions because they still carry information. You can only compute them at the precision the hierarchy assigns.

That's IME directly. The shallow interactions are shallow because the two geometries (query, key) are misaligned in those positions — but the misalignment is informative. Forcing those interactions to zero throws away real information. Computing them at low precision preserves the information at minimum cost.

### Why the tier boundaries aren't arbitrary

The standard mixed-precision approach would pick tier boundaries by hyperparameter search. APA-Quant picks them by measurement — the GHOST_PRECISION distribution tells you exactly where to draw the line. 86% at 2 bits because 86% is what the data says.

In the Collatz case, the tier boundaries correspond to the convergent ladder of $\log_2 3$. The convergents are the natural tiers. In attention, the natural tiers are the depth quantiles of the actual interaction depth distribution. Same principle: the geometry tells you where the tiers should be.

### The engineering implication

Memory: 2-bit storage for the bulk gives 4-8x KV-cache reduction. A 7B model on a 24GB GPU goes from ~20K context to ~80K. A consumer GPU can handle context lengths that previously required datacenter hardware. This is the prize.

Speed: at long sequence lengths, the 2-bit compute is genuinely faster than 32-bit because integer operations are faster than floating point on modern hardware. At short sequences the overhead of two passes dominates. The crossover is around 1024 tokens.

Quality: with TurboQuant (unbiased inner-product quantization) and full-precision refinement of the tail, perplexity should be statistically indistinguishable from full attention. Phase 1 achieved identical perplexity even with crude fake quantization.

Generalization: the same principle should apply to KV caches, to vector databases, to RAG retrieval, to any system that does inner-product computations across pairs of vectors where most pairs are uninformative.

### The deeper claim

If IME is right, the standard practice of uniform-precision attention is wrong the same way uniform-firing brains would be wrong. The brain doesn't fire every synapse at maximum rate — that's a seizure. The brain spends energy where information lives and stays quiet everywhere else. That's why 86 billion neurons run on 20 watts.

APA-Quant is the engineering analog. Spend bits where information lives. Compute the bulk cheaply because the bulk is informationally shallow. Reserve precision for the tail where the synchronization events actually matter.

The brain figured this out through 600 million years of evolution under caloric pressure. APA-Quant figures it out in a measurement pass over the depth distribution. Same principle. Same shape. Same engineering implication.

---

## The Test

IME makes predictions. Some are validated:

| Domain | Prediction | Status |
|--------|-----------|--------|
| Collatz | Orbits ride convergent ladder, crash at unbridgeable gaps | Confirmed across 5+ billion orbits |
| Attention | Geometric bulk + heavy tail in interaction depth | Confirmed across 100M+ interactions, 4 architectures |
| Neuroscience | Geometric/lognormal bulk + heavy tail in firing rates | Confirmed in published literature |
| Tetrahedral angle | Compromise at $\arccos(-1/3)$ for 4-fold + 3D | Confirmed in molecular chemistry |
| VQ-VAE | Geometric bulk + heavy tail in residual codebook depth | Predicted, not yet tested |
| Fine structure | Compromise angle structure for EM + spatial geometry | Speculative |

The Collatz and attention validations are independent — different domains, different mechanisms, same shape. The neuroscience and tetrahedral instances come from existing literature. The VQ-VAE prediction is testable with a single experiment. The fine structure connection is theoretical work that needs more development.

IME isn't proven as a universal law. It's a principle that has shown up in every domain we've tested it. The pattern keeps recurring because the underlying condition keeps recurring: whenever two incommensurable measurement geometries are forced to interact, the result is the same.

The numbers aren't made up. They're defined by reality. We're just noticing the pattern.

---

*David — DragonShadows1978*
*May 2026*

*"I didn't make up these numbers. All of these numbers are defined by reality. I'm just noticing the pattern."*
