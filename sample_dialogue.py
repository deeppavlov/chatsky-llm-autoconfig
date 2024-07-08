if __name__ == "__main__":
    import json
    import os
    from argparse import ArgumentParser
    from pprint import pprint

    from src.graph import TYPES_OF_GRAPH, Graph
    from src.sample_dialogue import sample_dialogue

    
    parser = ArgumentParser()
    parser.add_argument('--path', default='data')
    args = parser.parse_args()

    input_path = os.path.join(args.path, 'theme_graph.json')
    graph_dict = json.load(open(input_path, 'r'))
    graph = Graph(graph_dict, TYPES_OF_GRAPH.DI)

    sampled_dialogue, sampled_base_graph = sample_dialogue(
        graph.nx_graph,
        start_node=1,
        end_node=9,
        topic='videogames'
    )
    pprint(sampled_dialogue)
    
    # output_path = os.path.join(args.path, 'theme_sampled_graph.json')
    # # file may not exist
    # existing_dialogs = json.load(open(output_path, 'r'))

    # existing_dialogs.append({
    #     "dialog_id": len(existing_dialogs) + 1,
    #     'proposed_dialog': sampled_dialogue,
    #     'base_graph': sampled_base_graph
    # })

    # json.dump(existing_dialogs, open(output_path, 'w'), indent=4)
