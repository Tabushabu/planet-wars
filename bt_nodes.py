from copy import deepcopy
from random import choice
import logging
import re


from planet_wars import issue_order

def log_execution(fn):
    def logged_fn(self, state):
        logging.debug('Executing:' + str(self))
        result = fn(self, state)
        logging.debug('Result: ' + str(self) + ' -> ' + ('Success' if result else 'Failure'))
        return result
    return logged_fn

blackboard = {}

############################### Base Classes ##################################
class Node:
    def __init__(self, name, function, arguments):
        self.name = name
        self.function = function
        self.arguments = arguments
        self.localBlackboard = {}
        self.blackboard = blackboard

    @log_execution
    def execute(self, state):
        params = []
        for key, value in self.arguments.items():
            valid_argument, value = CheckForBlackboard(key, value)
            if not valid_argument:
                logging.info(f"Encountered invalid argument passed into {str(self)}")
                return False
            params.append(value)
        
        #logging.info(f"function being called: {self.function.__name__}, params: {params}")
        if len(params) > 0:
            return self.function(self, state, *params)
        return self.function(self, state)

    def copy(self):
        return deepcopy(self)
    
    def tree_to_string(self, indent=0):
        return '| ' * indent + str(self) + '\n'
    
    def __str__(self):
        return self.name
    
    def debug(self, message):
        pass
    
class Leaf(Node):
    def __init__(self, name, function, arguments):
        super().__init__(name, function, arguments)
    
class Decorator(Node):
    def __init__(self, name, function, arguments, child_node = None):
        super().__init__(name, function, arguments)
        self.child_node = child_node

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        if hasattr(self.child_node, 'tree_to_string'):
            string += self.child_node.tree_to_string(indent + 1)
        else:
            string += '| ' * (indent + 1) + str(self.child_node) + '\n'
        return string

class Composite(Node):
    def __init__(self, name, function, arguments, child_nodes=[]):
        super().__init__(name, function, arguments)
        self.child_nodes = child_nodes

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        for child in self.child_nodes:
            if hasattr(child, 'tree_to_string'):
                string += child.tree_to_string(indent + 1)
            else:
                string += '| ' * (indent + 1) + str(child) + '\n'
        return string


############################### Composite Nodes ##################################



############################# Decorator Nodes ###############################

class Precondition(Decorator):
    def __init__(self, child_node, condition_function, name=None):
        super().__init__(child_node, name)
        self.pre_condition = condition_function
        
    @log_execution
    def execute(self, state):
        if self.pre_condition(state):
            return self.child_node.execute(state)
        return False
    
    def __str__(self):
        return super().__str__() + " checks function " + str(self.pre_condition.__name__)



############################### Leaf Nodes ##################################

def CheckForBlackboard(key, variable):
    if variable is "" or variable is None: #provided key without variable
        logging.warn(f"parameter {key} is an empty string")
    
    if re.search("^out\d+$", key) is not None:
        return True, variable 
    
    if isinstance(variable, str) and len(variable) >= 2 and variable[0] == '{' and variable[-1] == '}':
        if variable in blackboard: # if an in variable
            return True, blackboard[variable]
        logging.warn(f"failed to find {variable} in blackboard.")
        return False, None # should be in the blackboard, but not
    return True, variable # if constant value argument
    
class Action(Leaf):
    pass

        
class TreeRoot(Node):
    def __init__(self, child_node, name):
        super().__init__(name, self.tree_root_execute, {})
        self.child_node = child_node
    
    def tree_root_execute(self, s, state):
        blackboard.clear()
        logging.debug("wiping blackboard")
        return s.child_node.execute(state)

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        if hasattr(self.child_node, 'tree_to_string'):
            string += self.child_node.tree_to_string(indent + 1)
        else:
            string += '| ' * (indent + 1) + str(self.child_node) + '\n'
        return string
    
