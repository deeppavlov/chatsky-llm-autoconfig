# Experiment name
Dialogue to graph generation

### Issues and goals
My understanding of reasons for this experiment is:
1. To integrate currently working algorithms of dialogue2graph generation (d2gg) into current project workflow.
2. To measure metrics of d2gg task and to keep them high with dataset evolution.

**The Most noticeable issues.**
1. To make gpt-4o-mini solve d2gg
2. Check current metrics algorithms for d2gg (triplet_match and is_same_structure)
3. Add embedding based comparison for utterances in triplet_match
4. Select embedding model
5. Getting criteria for such selection process

## Hypothesises and steps

Approaches we would try to solve the issues.

*We will try*
1-2. *prompt refinement with gpt-4o-mini, few-shot prompting, additional steps in CoT approach, try different models, fine-tuning*
3-4. *BGE-M3 based*
5. *With dataset evolution will be testing embedders*

## Results
Nov 19: general_graph_generation_prompt gives 3 out of 3 on short.json
BGE-M3 embedder and 0.13 threshold for "pairwise_embedding_distance" in langchain evaluator were used, but it gives 0.21 - problem on this pair:

"Welcome to tech support! How can I assist you today?"
"Just to confirm, you're requesting a double room for two nights, correct?"

So will try "BAAI/bge-reranker-v2-m3" cross encoder now, it shows better results for this pair

## Future plans
All things to be considered by future researchers, plans on next experiments and so on
