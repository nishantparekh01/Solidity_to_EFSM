Supremica = {}

# Events - contains list of all events
Supremica['Events'] = {}
Events = Supremica['Events']

# Components - contains all efsms
Supremica['Components'] = {}
Components = Supremica['Components']

# Variable Component - Contains all variables
Components['VariableComponent'] = {}
VariableComponent = Components['VariableComponent']
VariableComponent['EnumVariables'] = {}
VariableComponent['StructVariables'] = {}

# creating a dictionary to store all generated addresses
VariableComponent['AddressVariables'] = {}


class EFSM:
    """Class representing an Extended Finite State Machine (EFSM)."""

    def __init__(self, name):
        """Initializes the EFSM with a name."""
        self.name = name
        self.efsm = {'node_list': {}, 'edge_list': {}}
        self.node_list = self.efsm['node_list']
        self.edge_list = self.efsm['edge_list']
        self.i = 0
        self.current_node = 'S0'  # Start with the initial node S0
        self.node_list[self.current_node] = {}

    def create_transition(self, source, target, event, guard, action):
        """Creates a transition dictionary."""
        return {
            'source_node': source,
            'target_node': target,
            'event': event,
            'guard': guard,
            'action': action
        }

    def addTransition(self, transition):
        """Adds a transition to the edge_list and updates the current node."""
        self.edge_list[f't{self.i}'] = transition
        self.i += 1
        self.current_node = transition['target_node']  # Update the current node

