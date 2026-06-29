class StateMerger:

    def commit_batch(self, state, results, graph, layer=None):

        for node_name, output in results.items():
            state.node_outputs[node_name] = output

        return state