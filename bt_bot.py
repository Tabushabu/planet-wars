import xml.etree.ElementTree as ET
import bt_nodes
import behaviors
from functools import partial
from random import randint
from planet_wars import PlanetWars, finish_turn

import logging, traceback, sys, os, inspect

def initialize_logging(filename):
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    file_path = os.path.join(current_dir, "logs")
    full_name = os.path.join(file_path, f"{filename}.log")
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    logging.basicConfig(filename=full_name, filemode='w', level=logging.DEBUG, force=True)
    sys.path.append(file_path)

def parse_full_xml_tree(xml_path, behavior_tree_name):
    tree = ET.parse(xml_path) #parses xml file in specific path -- from xml.etree.elementTree
    root = tree.getroot()

    #behavior_tree_element = root.find(".//BehaviorTree") # finds 1st BT occurrence
    #if behavior_tree_element is None:
    #    print("Error: Behavior tree node not found.") #boink
    #    return None

    trees = {}
    for bt in root.findall("BehaviorTree"):
        if bt in trees:
            continue

        subtree_name = bt.get("ID")
        logging.info("tree:", subtree_name)
        tree = bt_nodes.TreeRoot(parse_node(bt[0]), name=subtree_name)
        trees[subtree_name] = tree
        logging.info(tree.tree_to_string())

    if behavior_tree_name in trees:
        return trees[behavior_tree_name]
    return trees[0]

def parse_node(node):
    node_title = node.tag
    arguments = node.attrib 
    if node_title in behaviors.action_lookup_table:
        return bt_nodes.Action(node_title, behaviors.action_lookup_table[node_title], arguments)
    if node_title in behaviors.composite_lookup_table:
        return bt_nodes.Composite(node_title, behaviors.composite_lookup_table[node_title], arguments, [parse_node(c) for c in node])
    if node_title in behaviors.decorator_lookup_table:
        return bt_nodes.Decorator(node_title, behaviors.decorator_lookup_table[node_title], arguments, parse_node(node[0]))
    
    logging.info(f"Failed to resolve node: {node_title}")

    return None

def do_turn(state):
    return behavior_tree.execute(state)

    
# main function to run the code
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Invalid parameters, expected xml file and tree name.")
        exit(1)

    xml_path = sys.argv[1]
    behavior_tree_name = sys.argv[2]
    initialize_logging(behavior_tree_name)
    
    logging.info("starting main")
    behavior_tree = parse_full_xml_tree(xml_path, behavior_tree_name)
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                logging.info("starting turn")
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")