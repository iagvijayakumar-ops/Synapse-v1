import uuid
from typing import List, Dict, Set
from models.skill_tree import SkillTree, Node, Edge, NodeState

def validate_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """
    Validates if the graph is a Directed Acyclic Graph (DAG) using iterative DFS.
    """
    adj = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source in adj:
            adj[edge.source].append(edge.target)
    
    visited = set()
    path = set()
    
    for node in nodes:
        if node.id in visited:
            continue
            
        stack = [(node.id, False)]
        while stack:
            curr_id, processed = stack.pop()
            
            if processed:
                path.remove(curr_id)
                continue
                
            if curr_id in path:
                return False  # Cycle detected
            if curr_id in visited:
                continue
                
            visited.add(curr_id)
            path.add(curr_id)
            stack.append((curr_id, True))
            
            for neighbor in adj.get(curr_id, []):
                stack.append((neighbor, False))
                
    return True

def build_graph(raw_json: dict, topic: str, session_id: str) -> SkillTree:
    """
    Parses nodes and edges, sets initial states, and validates DAG.
    """
    nodes = []
    for n in raw_json.get("nodes", []):
        nodes.append(Node(
            id=n["id"],
            label=n["label"],
            description=n["description"],
            prerequisites=n.get("prerequisites", []),
            state=NodeState.LOCKED
        ))
        
    edges = [Edge(source=e["source"], target=e["target"]) for e in raw_json.get("edges", [])]
    
    # Initialize state: Nodes with no prerequisites are ACTIVE
    for node in nodes:
        if not node.prerequisites:
            node.state = NodeState.ACTIVE
            
    if not validate_dag(nodes, edges):
        raise ValueError("The generated graph contains cycles and is not a valid DAG.")
        
    return SkillTree(
        session_id=session_id,
        topic=topic,
        nodes=nodes,
        edges=edges
    )

def get_unlockable_nodes(tree: SkillTree) -> List[str]:
    """
    Returns IDs of LOCKED nodes whose prerequisites are all MASTERED.
    """
    mastered_ids = {node.id for node in tree.nodes if node.state == NodeState.MASTERED}
    unlockable = []
    
    for node in tree.nodes:
        if node.state == NodeState.LOCKED:
            if all(pre in mastered_ids for pre in node.prerequisites):
                unlockable.append(node.id)
    return unlockable

def unlock_after_mastery(tree: SkillTree, mastered_node_id: str) -> List[str]:
    """
    Marks a node as MASTERED and unlocks eligible dependent nodes.
    """
    newly_activated = []
    for node in tree.nodes:
        if node.id == mastered_node_id:
            node.state = NodeState.MASTERED
            break
            
    unlockable_ids = get_unlockable_nodes(tree)
    for node in tree.nodes:
        if node.id in unlockable_ids:
            node.state = NodeState.ACTIVE
            newly_activated.append(node.id)
            
    return newly_activated

def create_bridge_node(tree: SkillTree, failed_node_id: str) -> Node:
    """
    Creates a simpler bridge node for a concept that the user is struggling with.
    """
    original_node = next((n for n in tree.nodes if n.id == failed_node_id), None)
    if not original_node:
        raise ValueError("Failed node not found")
        
    bridge_id = f"bridge_{failed_node_id}_{uuid.uuid4().hex[:6]}"
    bridge_node = Node(
        id=bridge_id,
        label=f"Foundation: {original_node.label}",
        description=f"A simplified introductory lesson to help master {original_node.label}.",
        state=NodeState.ACTIVE,
        prerequisites=original_node.prerequisites.copy(),
        is_bridge=True,
        parent_node_id=failed_node_id
    )
    
    # Add bridge node to tree
    tree.nodes.append(bridge_node)
    
    # Add edge from bridge to failed node
    tree.edges.append(Edge(source=bridge_id, target=failed_node_id))
    
    # Update failed node to have bridge as prerequisite
    original_node.prerequisites.append(bridge_id)
    original_node.state = NodeState.LOCKED
    
    return bridge_node
