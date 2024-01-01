import xml.etree.ElementTree as ET
import bt_nodes
import behaviors


# parsing xml BTS
def parse_xml_tree(xml_path):
    tree = ET.parse(xml_path) #parses xml file in specific path -- from xml.etree.elementTree
    root = tree.getroot()

    behavior_tree_element = root.find(".//BehaviorTree") # finds 1st BT occurrence
    root_node_element = behavior_tree_element.find("*")
    if root_node_element is None:
        print("Error: Root node element not found under BehaviorTree.")
        return None

    root_node = parse_node(root_node_element, root)
    return root_node


def parse_node(node_element, root):
    node_type = node_element.tag

    composite_class = bt_nodes.node_type_to_class.get(node_type)

    if composite_class and issubclass(composite_class, bt_nodes.Composite): #issubclass - checks if a class is a subclass of another class
        children = [parse_node(child, root) for child in node_element]
        return composite_class(children, name=node_type)

    elif node_type == "Action":
        action_id = node_element.get("ID")
        attributes = {attr.get("name"): attr.get("default") for attr in node_element.findall("*[@name]")}
        return bt_nodes.Action(action_id, attributes)

    else:
        model_element = root.find(f"./TreeNodesModel/Action[@ID='{node_type}']")
        if model_element is not None:
            attributes = {attr.get("name"): attr.get("default") for attr in model_element.findall("*[@name]")}
            return bt_nodes.Action(node_type, attributes)
        else:
            print(f"Unknown node type: {node_type}")
            return None


def print_behavior_tree(node, level=0):
    # prints the behavior tree in the standard format
    indentation = "  " * level
    if isinstance(node, bt_nodes.Sequence):
        print(f"{indentation}Sequence:")
        for child in node.child_nodes:
            print_behavior_tree(child, level + 1)
    if isinstance(node, bt_nodes.Selector):
        print(f"{indentation}Fallback:")
        for child in node.child_nodes:
            print_behavior_tree(child, level + 1)
    if isinstance(node, bt_nodes.Random_Selector):
        print(f"{indentation}Random Fallback:")
        for child in node.child_nodes:
            print_behavior_tree(child, level + 1)
    if isinstance(node, bt_nodes.Random_Sequence):
        print(f"{indentation}Random Sequence:")
        for child in node.child_nodes:
            print_behavior_tree(child, level + 1)
            
    elif isinstance(node, bt_nodes.Action):
        print(f"{indentation}- {node}")
        
        

# main function to run the code
if __name__ == "__main__":
    xml_path = "test_groot.xml"
    behavior_tree_root = parse_xml_tree(xml_path)

    if behavior_tree_root:
        print("\nBehavior Tree Structure:")
        print_behavior_tree(behavior_tree_root)