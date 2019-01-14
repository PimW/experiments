import re
import os


def extract_constraints():
    pass


def write_constraints_as_sat():
    pass


def extract_bdd_nodes(filename: str) -> [set, list]:
    """
    The file contains all nodes of the bdd in the format:

    ::

        [
            node(node_id, var, low, high),
            node(node_id, var, low, high),
            ...
        ], [bdd_id,...]


    To parse the file we skip the first line. For each line after we extract
    the node information using a regular expression. Each node is added to a set
    to remove duplicates. When we reach the last line of the file containing
    the id's of the nodes that represent the outputs, we stop the iteration.

    :param filename: name of the file containing the bdd.
    :return: set containing all the bdd nodes in tuple format.

    """
    bdd_nodes = set()
    outputs = list()

    file = open('/home/pim/bdd-export/' + filename)

    file.readline()  # skip opening bracket
    for line in file.readlines():
        if line[0] == "]":
            outputs = line.split(',')[1:-1]
            break
        print(line.strip(), end=" ")

        # tuple contents (node_id, var, low, high)
        node_tuple = re.search('node\((\d+),(\d+),(\d+),(~?\d+)\)', line).groups()

        print("==>", node_tuple)
        bdd_nodes.add(node_tuple)

    return bdd_nodes, outputs


def convert_bdd_to_sat(bdd_nodes: set) -> dict:
    """
    This function converts a bdd to a sat-circuit. A bdd already has a
    circuit like structure. This means can directly convert each bdd node
    to a configuration of logical gates.
    Each node is a tuple of the form: (node_id, var, low, high)
    The low branch is taken if !<var> the high branch if <var> (is true)

    There are 3 possible cases for a bdd node:

    1. (node_id, var, 0, ~0) or (node_id, var, ~0, 0) which means both branches \
        of a node go to true or false, this node is equivalent to <var> or !<var> \
        respectively.

    2. (node_id, var, 0, high_id), (node_id, var, ~0, high_id), (node_id, var, low_id, 0) \
        or (node_id, var, low_id, ~0). This type of node has one branch to a different node \
        and one branch to either true or false. \
        These nodes are equivalent to:
            | <node_id> = <var> & <low_id>
            | <node_id> = !<var> | (<var> & <high_id>)
            | <node_id> = !<var> & <low_id>
            | <node_id> = <var> | (!<var> & <low_id>)

    3. (node_id, var, low_id, high_id) in this case both branches go to different bdd nodes. \
        This results in:
        <node_id> = (!<var> & <low_id>) | (<var> & <high_id>)

    This can be reduced to the cases for internal nodes and leaves:

    1. node_id != 0 and node_id != ~0: then <node_id> = (!<var> & <low_id>) | (<var> & <high_id>) \
        which is equivalent to the 3rd case in the previous definition.

    2. node_id = 0: then !<node_id>

    3. node_id = ~0: then <node_id>

    This does however lead to more redundancy in the final circuit for the true and false nodes.

    Each bdd node will be converted to the form:

    ::

        {
            <node_id> : ('|', <left_id>, <right_id>),
            <left_id> : ('&', !<var>, <low_id>),
            <right_id> : ('&', <var>, <high_id>),
            ...
        }

    where left_id and right_id are new id's that do not exist yet.

    :param bdd_nodes: Set of BDD nodes
    :return: SAT circuit represented in a dict

    """
    sat_circuit = dict()
    node_id_counter = max([int(n[0]) for n in bdd_nodes])
    node_id_counter += 1

    for node_tuple in bdd_nodes:
        (node_id, var, low, high) = node_tuple

        left_id = node_id_counter
        node_id_counter += 1
        right_id = node_id_counter
        node_id_counter += 1

        sat_circuit[left_id] = ('&', '!' + var, low)
        sat_circuit[right_id] = ('&', var, high)

        sat_circuit[node_id] = ('|', left_id, right_id)

    return sat_circuit


def convert_circuit_to_aig(sat_circuit: dict) -> dict:
    """
    This function converts a sat circuit to a And/Inverter Graph.
    And/Inverter Graphs are circuits that only contain AND-gates and NOT-gates.
    Each AND-gate has exactly 2 inputs. To convert the circuit to and AIG we
    just have to replace the 'or' gates with 'and' gates using de morgan's rule.
    If we have (a | b) this becomes !(!a & !b), which contains only 'and' and 'not'.
    Since 'a' and 'b' are already just id's of the left and right inputs of the not gate.
    We can directly transform without introducing more gates.

    Any double negation that this function introduces will also be removed to simplify
    the resulting AIG.

    :param sat_circuit: Sat circuit in dict format.
    :return: The sat circuit transformed to an AIG.
    """

    for gate_id, gate in sat_circuit.items():
        if gate[0] == '|':
            sat_circuit[gate_id] = ('!&',
                                    ('!' + gate[1]).replace('!!', ''),
                                    ('!' + gate[2]).replace('!!', ''))
    return sat_circuit


def write_AIG_as_AIGER(vars: list, outputs: list, aig: dict) -> str:
    """
    Write AIG to file using the AIGER standard (http://fmv.jku.at/papers/Biere-FMV-TR-07-1.pdf),
    this standard encodes an AIG in an ASCII file format.

    The file has a header containing the information necessary for parsing the file,
    the format is:
    aag <max variable index> <inputs> <latches> <outputs> <AND-gates>

    All following lines of the file contain (in order):
    - Inputs
    - Outputs
    - Gates

    Each input and output is represented by a variable id that is an even number. The inverse of
    each variable is represented by <id> + 1 (inverter bit). 0 represents false and 1 is the
    inverse and represents true.
    AND-gates are represented by <gate id> <left> <right>, to invert the inputs we just have to
    add 1 to the id's. The output of the gate can be inverted where it is used as input or as
    final output of the circuit.
    An example for (1 | 2) (which is equivalent to !(!1 & !2):

    ::

        aag 3 2 0 1 1
        2               # input 0
        4               # input 1
        7               # output 0 -> !(!1 & !2) :: !6 = 6 + 1
        6 3 5           # AND gate 0 (id: 6)-> !1 & !2

    Optionally at the end of the file a symbol table can be added to show which inputs and outputs
    correspond to which variables.

    To keep it simple we will just multiply each variable id in the circuit by 2 and add 1 if the
    variable is negated.

    The output of each gate is non-negated in the output format, however the operators in the aig
    dict can be negated. This problem can be solved by checking if the input gates are inverted by
    checking their operators. Then we can add the negation on the input it is used for or remove a
    possible double negation.

    :param vars: List of variables that are not gates.
    :param outputs: List of nodes that are outputs.
    :param aig: Complete representation of the AIG in dict format.
    :return: AIGER formatted string for the AIG.
    """
    aiger_string = ""

    max_var_index = 0  # max(vars * 2)?
    input_count = 0  # len(vars)?
    output_count = 0  # 1?
    gate_count = 0  # len(aig.keys)?

    variables_string = ""
    gates_string = ""
    outputs_string = ""
    symbol_string = ""  # not used yet

    for var in vars:
        variables_string += "%d\n" % (int(var) * 2)

        # update relevant header data
        if var * 2 > max_var_index:
            max_var_index = var * 2

        input_count += 1

    for output in outputs:
        output_id = int(output) * 2

        if output not in vars:
            if aig[output][0][0] == '!':  # and left.op starts with a negation
                output_id += 1
        outputs_string += "%d\n" % output_id
        output_count += 1

    for gate_id, gate in aig:
        (op, left, right) = gate

        left_inverse = 0
        if left[0] == '!':
            left_id = int(left[1:]) * 2
            left_inverse += 1
        else:
            left_id = int(left) * 2
        if left.strip('!') not in vars:  # if left is a gate
            if aig[left.strip('!')][0][0] == '!':  # and left.op starts with a negation
                left_inverse += 1
        left_id += (left_inverse % 2)  # remove double negation

        right_inverse = 0
        if right[0] == '!':
            right_id = int(right[1:]) * 2
            right_inverse += 1
        else:
            right_id = int(right) * 2
        if right.strip('!') not in vars:  # if left is a gate
            if aig[right.strip('!')][0][0] == '!':  # and left.op starts with a negation
                right_inverse += 1
        right_id += (right_inverse % 2)  # remove double negation

        gates_string += "%d %d %d" % (int(gate_id) * 2, left_id, right_id)
        gate_count += 1

    aiger_string += "aag %d %d 0 %d %d" % (max_var_index, input_count, output_count, gate_count)
    aiger_string += variables_string
    aiger_string += outputs_string
    aiger_string += gates_string
    aiger_string += symbol_string

    return aiger_string


def convert_file(filename) -> str:
    """
    """
    sub_expression = ""
    print("Converting file: " + filename)
    sub_expression += "# " + filename.split('/')[-1] + "\n"

    bdd_nodes, outputs = extract_bdd_nodes(filename)

    variables = [node[1] for node in bdd_nodes]

    circuit = convert_bdd_to_sat(bdd_nodes)
    aig = convert_circuit_to_aig(circuit)

    aiger_string = write_AIG_as_AIGER(variables, outputs, aig)

    return sub_expression


if __name__ == "__main__":
    reachable_states_expression = ""
    transition_relation_expression = ""
    initial_states_expression = ""

    for bdd_file in os.listdir('/home/pim/bdd-export/'):
        if 'states' in bdd_file:
            reachable_states_expression += convert_file(bdd_file)
        elif 'rel' in bdd_file:
            transition_relation_expression += convert_file(bdd_file)
        elif 'init' in bdd_file:
            initial_states_expression += convert_file(bdd_file)

    with open("initial-states.sat", "w") as f:
        f.write(initial_states_expression)

    with open("reachable-states.sat", "w") as f:
        f.write(reachable_states_expression)

    with open("transition-relation.sat", "w") as f:
        f.write(transition_relation_expression)
