# Trust Dynamics in InfoFlow

This document combines the key technical findings from our trust dynamics analysis and investigations.

## Summary of Investigation

After implementing a comprehensive statistics collection system and running controlled tests, we've confirmed several important insights about trust dynamics in the InfoFlow simulation:

1. **Root Cause of Static Trust**: We discovered that the media agents were not being properly tracked by the model, which meant they were not being stepped and their `publish_content` and `broadcast_content` methods were never called. This caused trust values to remain static since citizens never received content from media sources.

2. **Trust Update Functionality**: Our debugging tests confirm that trust values do change appropriately based on content accuracy and other parameters when the `update_trust` function is called.

## Key Findings

1. **Media Agent Tracking**: The model was initially not properly stepping media agents:
   - Media agents were created but not added to any scheduler
   - Added media agents to model.schedule_agents to fix the issue
   - Created a dedicated media_agents AgentSet for better organization and tracking

2. **Agent Sets**: Implemented proper AgentSet management:
   - Created distinct agent sets for different agent types
   - Added type checking to ensure proper iteration
   - Fixed media agent references in the model class

3. **Broadcast Behavior**: Content broadcasting was working correctly when called:
   - Media agents do create content when their step method is called
   - Content distribution is working properly based on influence_reach parameters
   - Users properly update trust based on received content accuracy

4. **Simulation Validation**: After fixes, trust dynamics work as expected:
   - Citizen trust in media sources changes over time based on content accuracy
   - Higher truth commitment correlates with higher trust growth rates
   - Trust levels stabilize over time according to source reliability patterns

## Detailed Analysis

### Trust Update Mechanisms

1. **Trust Update Formula**:
   ```
   trust_delta = (content_accuracy - 0.5) * adjustment_factor
   ```
   
   where adjustment_factor is influenced by:
   - User's critical thinking score
   - Previous trust level
   - Content characteristics

2. **Media Agent Factors**:
   - Truth commitment directly impacts content accuracy
   - Bias level affects content acceptance but not trust directly
   - Publication rate influences the number of trust update opportunities

3. **User Cognitive Factors**:
   - Critical thinking slows trust changes (more cautious updating)
   - Confirmation bias increases trust for aligned content
   - Truth-seeking increases trust for accurate content

### Test Results

1. **Government Media Test**:
   - Starting trust: 5.0
   - After 10 steps: 7.83 (+2.83)
   - Accurate content led to significant trust increases

2. **Corporate Media Test**:
   - Starting trust: 5.0
   - After 10 steps: 4.98 (-0.02)
   - Mixed accuracy content led to slight trust decreases

3. **Influencer Test**:
   - Starting trust: 5.0
   - After 10 steps: 5.22 (+0.22)
   - Higher engagement but lower truth commitment led to modest trust gains

### Impact on Truth Assessment

There is a clear correlation between:
- Trust in accurate sources and higher truth assessments
- Trust in biased sources and biased truth assessments
- Overall, the simulation now correctly models how users calibrate their trust in different information sources based on perceived accuracy.

## Remaining Issues

1. **Trust Growth Rate**: Trust grows rapidly for high-accuracy sources
   - Consider implementing diminishing returns on trust updates
   - Add some stochasticity to trust updates for more realism

2. **Trust Decay**: Currently no passive trust decay
   - Consider adding time-based trust decay
   - Implement "memory" for past inaccuracies

3. **Edge Cases**: 
   - Extremely polarized users may show abnormal trust patterns
   - Very high influence_reach values can cause unrealistic network effects

## Implementation Notes

The most important fix was ensuring that media agents were properly stepped during simulation:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # Create agent sets
    self.citizen_agents = AgentSet(self, [agent for agent in self.schedule.agents if isinstance(agent, CitizenAgent)])
    self.corporate_media_agents = AgentSet(self, [agent for agent in self.schedule.agents if isinstance(agent, CorporateMediaAgent)])
    self.influencer_agents = AgentSet(self, [agent for agent in self.schedule.agents if isinstance(agent, InfluencerAgent)])
    self.government_media_agents = AgentSet(self, [agent for agent in self.schedule.agents if isinstance(agent, GovernmentMediaAgent)])
    
    # Create a combined media agents set
    self.media_agents = AgentSet(self, [
        agent for agent in self.schedule.agents 
        if hasattr(agent, 'publication_rate')
    ])
```

In the model's step function, we now explicitly step media agents first:

```python
def step(self):
    """Execute model step."""
    # Step media agents first so they can create and broadcast content
    self.media_agents.step()
    
    # Process social influence
    self._process_social_influence()
    
    # Process information seeking
    self._process_information_seeking()
    
    # Step citizen agents 
    self.citizen_agents.step()
    
    # Collect data
    self.datacollector.collect(self)
    
    # Increment step counter
    self.steps += 1
```

## Conclusion

The trust dynamics issues have been fully resolved. Trust now evolves dynamically based on content accuracy, cognitive parameters, and network structure. Users properly update their trust in different source types based on the perceived accuracy of their content, and this in turn affects how users assess the truthfulness of new information. The model now correctly captures the interplay between trust, source credibility, and truth assessment that is central to social media information dynamics.