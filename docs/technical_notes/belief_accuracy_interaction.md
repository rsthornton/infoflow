# Truth Assessment, Accuracy, and Bias: Design Decisions

## Understanding the Interaction Between Truth Assessment and Political Bias

> Note: This document uses "truth assessment" and "belief" interchangeably. We recommend standardizing to "truth assessment" in future versions as it more clearly describes the agent's evaluation of how true a claim is on a 0-1 scale.

During the development of the InfoFlow 2.0 model, we encountered an interesting philosophical question that affected our implementation:

> How should a truth-seeking agent update their assessment of truth when they receive information from a source with a particular political bias?

This document captures our reasoning and design decisions on this matter, which could be valuable for future iterations or other models addressing similar questions.

## The Challenge

Our model includes:

- **Citizens with beliefs** on a 0-1 scale representing how true they think claims are (0.5 is neutral/uncertain)
- **Media agents with political bias** on a -5 to +5 scale (anti-Trump to pro-Trump)
- **Content with accuracy** on a 0-1 scale (how factual it is)
- **Truth-seeking agents** (+2 to +5 on the truth-seeking scale) who prioritize accuracy
- **Truth-avoiding agents** (-2 to -5 on the truth-seeking scale) who prioritize confirmation

When a truth-seeking agent receives content from a source with a strong political leaning, how should their assessment of that content's truth value update? There are several reasonable approaches:

## Possible Approaches

### 1. Independent Assessment

In this approach, agents would:
- Evaluate content accuracy independently of political bias
- Update trust in the source based on accuracy
- Political bias has no effect on truth assessment

This approach makes sense if we view political leaning as completely separate from factual accuracy. An agent could recognize "This source has a strong political leaning, but I can still assess the truth of their claims objectively."

### 2. Bias-Distorted Perception

In this approach:
- Political bias acts as a filter that distorts perception of accuracy
- Strong political bias (in either direction) reduces perceived accuracy
- Truth-seeking agents are less affected by this distortion

This approach assumes that political bias creates a "lens" through which information is perceived, affecting an agent's ability to accurately assess truth.

### 3. Nuanced Interaction

This approach recognizes that:
- Accuracy and bias interact in complex ways
- Truth-seeking agents can better separate bias from accuracy
- Truth-avoiding agents are more influenced by confirmation bias

## Our Implementation Decision

We chose a model similar to #2 (Bias-Distorted Perception), with elements of #3. Specifically:

```python
# Calculate how political bias affects perception of accuracy
# Strong bias in either direction can distort perception of truth
bias_distortion = abs(content_bias) / 10.0  # 0-0.5 scale based on bias magnitude

# Truth-seeking agents are less affected by political bias
bias_distortion = bias_distortion * (1 - (truth_seeking_factor * 0.5))

# Calculate perceived accuracy (accuracy distorted by political bias)
perceived_accuracy = content_accuracy * (1 - bias_distortion)

# Target belief is primarily based on perceived accuracy (truth value)
target_belief = perceived_accuracy
```

Key points of our implementation:

1. **Bias distorts perception**: Stronger political bias (in either direction) makes it harder to perceive true accuracy
2. **Truth-seeking reduces distortion**: Truth-seekers are better at seeing through bias to assess true accuracy
3. **Belief represents truth assessment**: The ultimate belief value represents how true the agent thinks the content is

## Implications

This design decision has several interesting implications:

### 1. Highly Biased Content Is Less Effective at Conveying Truth

In our model, even when content is objectively accurate, high political bias (in either direction) reduces its effectiveness at conveying truth. This suggests a trade-off between persuasiveness through strong framing and effectiveness at conveying factual information.

### 2. Truth-Seeking Reduces Bias Effects

Agents with high truth-seeking values are less affected by political bias and can better assess the actual accuracy of content. This creates a protective effect against bias-induced distortion, allowing them to extract truth even from heavily biased sources.

### 3. Bias Creates Perception Gaps

Two agents viewing the same piece of content may form very different assessments of its truthfulness based on their truth-seeking values and how they process political bias. This creates perception gaps that can be difficult to bridge.

### 4. Complexity of Truth Assessment

The model shows how an agent's assessment of truth is affected by:
- Their inherent truth-seeking tendency
- The actual accuracy of information
- The political bias of sources they're exposed to
- Their confirmation bias and prior beliefs

This creates complex, emergent behavior where individual truth assessments evolve based on information environment.

## Future Refinements

For future iterations, we might consider:

1. **Memory factors**: How truth assessments stabilize or change based on the history of accurate/inaccurate information
2. **Competing claims**: How agents might handle accurate but contradictory claims from sources with opposite biases
3. **Distinguishing types of bias**: Different distortion effects for bias in conclusion vs. bias in framing/presentation
4. **Backfire effects**: When contradictory information strengthens rather than weakens existing truth assessments
5. **Multiple claims tracking**: Having agents maintain separate belief values for different claims/topics

## Conclusion

Our implementation resolves the philosophical question by modeling a world where political bias can distort perception of objective truth, but where truth-seeking ability can help overcome this distortion. The belief value in our model represents an agent's assessment of how true or false content is, not their political position.

This approach creates a complex but intuitively reasonable model of how truth assessments evolve in response to information of varying accuracy and bias. It captures the fundamentally different concepts of "what is objectively true" (content accuracy), "what political bias is present" (framing bias), and "what the agent believes is true" (belief value).

This decision significantly impacts the emergent behavior of our model and reflects a specific theory about how human truth assessment works in the real world. Alternative approaches might be equally valid for different research questions or theoretical frameworks.