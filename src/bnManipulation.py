import pysmile_license

class BNManipulation():
    def __init__(self):
        pass

    @staticmethod
    def print_cpt_matrix(self, net, node_handle):
        cpt = net.get_node_definition(node_handle)
        parents = net.get_parents(node_handle)
        dim_count = 1 + len(parents)

        dim_sizes = [0] * dim_count
        for i in range(0, dim_count - 1):
            dim_sizes[i] = net.get_outcome_count(parents[i])
        dim_sizes[len(dim_sizes) - 1] = net.get_outcome_count(node_handle)

        coords = [0] * dim_count
        for elem_idx in range(0, len(cpt)):
            BNManipulation.index_to_coords(elem_idx, dim_sizes, coords)

            outcome = net.get_outcome_id(node_handle, coords[dim_count - 1])
            out_str = "    P(" + outcome

            if dim_count > 1:
                out_str += " | "
                for parent_idx in range(0, len(parents)):
                    if parent_idx > 0:
                        out_str += ","
                    parent_handle = parents[parent_idx]
                    out_str += net.get_node_id(parent_handle) + "=" + \
                               net.get_outcome_id(parent_handle, coords[parent_idx])

            prob = cpt[elem_idx]
            out_str += ")=" + str(prob)
            print(out_str)

    @staticmethod
    def index_to_coords( self,index, dim_sizes, coords):
        """
        # Turns list of parameters into 2-D array
        :param index:
        :param dim_sizes:
        :param coords:
        """
        prod = 1
        len_dim_sizes = len(dim_sizes)
        range_dim_sizes = range(len_dim_sizes - 1, -1, -1)
        for i in range_dim_sizes:
            coords[i] = int(index / prod) % dim_sizes[i]
            prod *= dim_sizes[i]

    @staticmethod
    def updateNodeOutcomes(net, nodeId, outcomes):
        handle = net.get_node(nodeId)
        initial_outcome_count = net.get_outcome_count(handle)
        for i in range(0, initial_outcome_count):
            net.set_outcome_id(handle, i, outcomes[i])
        for i in range(initial_outcome_count, len(outcomes)):
            net.add_outcome(handle, outcomes[i])