# Cycle graph generation and augmentation of the synthetic dialogues

### Issues and goals

The main challenge was creating logically coherent and diverse synthetic dialogues at scale for tasks like chatbot training. The approach uses a cycle graph structure where dialogues must logically return to their starting point, enabling continuous conversation flows.

## Hypotheses and steps

The approach consists of:

1. **Cycle Graph Generation**
- GPT-4 mini was unable to generate valid cycle graphs consistently
- Requires larger models like GPT-4 to create JSON-structured dialogue graphs
- Enforces strict rules:
  - Must be cyclic with last edge connecting back to first node
  - Each node contains assistant utterances
  - Each edge contains user utterances  
  - Transitions must be logically coherent
  - Utterances in same list must be synonymous but differently worded

2. **Graph Validation** 
- Validates each transition triplet using GPT-4 mini
- Checks if source -> edge -> target transitions make logical sense
- Returns validation results with explanations of any issues
- Maps node IDs and validates their existence

3. **Dialogue Sampling**
- Uses DialogueSampler to generate complete dialogues from valid graphs
- Maintains conversation flow by following graph paths

4. **Dialogue Augmentation**
- Takes sampled dialogues and generates variations
- Creates 2-3 alternatives for each utterance while:
  - Maintaining same meaning/intent
  - Using different phrasing
  - Keeping theme consistency
  - Ensuring natural conversation flow

## Results

The implementation demonstrates:
- A cycle graph generation pipeline with validation
- A dialogue sampling system
- An initial augmentation framework

## Future plans

1. Integration into the main library
