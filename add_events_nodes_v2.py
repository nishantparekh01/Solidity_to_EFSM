import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, List, Tuple, Set

from ast_restructure import *  # expects: final_result, add_transition_to_xml, add_nodes_to_xml, etc.

pre_supremica = final_result

EventDeclList = ET.Element("EventDeclList")
event_list = []

INITIAL_NODE = "S0"


def add_events_to_xml(event: str):
    global EventDeclList, event_list
    if event not in event_list:
        event_list.append(event)
        ET.SubElement(EventDeclList, "EventDecl", Kind="UNCONTROLLABLE", Name=event)


# ----------------------------
# Node bookkeeping
# ----------------------------
node_id = 0
node_list = []


def check_node_already_created(node: str) -> bool:
    return node in node_list


def get_new_node(node_type: str) -> str:
    global node_id, node_list

    if node_type == "source":
        return "S" + str(node_id)

    if node_type == "source_reduced":
        prev = node_id - 1
        if prev < 0:
            prev = 0
        return "S" + str(prev)

    if node_type == "target":
        node_id += 1
        t_node = "S" + str(node_id)
        if check_node_already_created(t_node):
            return get_new_node("target")
        node_list.append(t_node)
        return t_node

    raise ValueError(f"Unknown node_type={node_type}")


def add_node_to_efsm_node_list(source_node: str, target_node: str):
    if source_node not in efsm_node_list:
        efsm_node_list.append(source_node)
    if target_node not in efsm_node_list:
        efsm_node_list.append(target_node)


def ttype(tr: dict) -> str:
    return tr.get("transition_type") or tr.get("type") or ""


# ----------------------------
# IF / ELSE stack logic
# ----------------------------
@dataclass
class NodePair:
    start: str
    end: Optional[str] = None


def _ensure_end(pair: NodePair) -> str:
    if pair.end is None:
        pair.end = get_new_node("target")
    return pair.end


def _normalize_if_markers(k: str) -> str:
    if k == "nested_true_body_start":
        return "true_body_start"
    if k == "nested_false_body_start":
        return "false_body_start"
    return k


def _ensure_user_invocation_node() -> str:
    """
    Enforce that user_invocation always targets S1.
    """
    global node_id, node_list

    if node_id == 0:
        return get_new_node("target")  # creates S1

    if "S1" not in node_list:
        node_list.append("S1")
    if node_id < 1:
        node_id = 1
    return "S1"


# ----------------------------
# Main
# ----------------------------
for efsm in pre_supremica["Components"]:
    node_id = 0
    efsm_node_list = []
    node_list = []

    if efsm == "VariableComponent":
        continue
    if "edge_list" not in pre_supremica["Components"][efsm]:
        continue

    edge_dict = pre_supremica["Components"][efsm]["edge_list"]
    n_transitions = len(edge_dict)
    EdgeList = ET.Element("EdgeList")

    # ---- single transition
    if n_transitions == 1:
        tr = edge_dict["t0"]

        # Respect locked nodes if already provided
        if tr.get("source_index") and tr.get("target_index"):
            source_node = tr["source_index"]
            target_node = tr["target_index"]
        else:
            source_node = INITIAL_NODE
            target_node = source_node
            tr["source_index"] = source_node
            tr["target_index"] = target_node

        add_node_to_efsm_node_list(source_node, target_node)

        if not tr.get("events"):
            event_name = str(efsm + "1")
            tr["event"] = event_name
            add_events_to_xml(event_name)
        else:
            for event_name in tr["events"]:
                add_events_to_xml(event_name)

        EdgeList.append(add_transition_to_xml(tr))

    # ---- multiple transitions
    else:
        node_pair_stack: List[NodePair] = []
        pending_else: Optional[NodePair] = None

        current_node = INITIAL_NODE

        # special bookkeeping
        sender_transfer_node = ""
        transfer_success_source_node = ""
        sender_transfer_merge_node = ""
        temporary_source_node = ""
        require_node = ""

        prev_k = None

        # transfer fail bookkeeping
        last_transfer_fail_edge: Optional[Tuple[str, str]] = None

        ordered_transitions: List[dict] = []
        locked_ids: Set[int] = set()

        for i in range(n_transitions):
            tr = edge_dict[f"t{i}"]
            raw_k = ttype(tr)
            k = _normalize_if_markers(raw_k)

            locked = bool(tr.get("source_index")) and bool(tr.get("target_index"))
            if locked:
                locked_ids.add(id(tr))
                src = tr["source_index"]
                tgt = tr["target_index"]

                # --- Update internal state so subsequent edges wire correctly (without changing src/tgt)
                if k == "user_invocation":
                    # invocations are external edges; only move sequential flow to S1 if we're still at S0
                    if current_node == INITIAL_NODE:
                        current_node = tgt

                elif k == "true_body_start":
                    # else-if inheritance
                    inherited_merge = None
                    if prev_k == "false_body_start" and pending_else is not None:
                        inherited_merge = pending_else.end
                        pending_else = None
                    node_pair_stack.append(NodePair(start=src, end=inherited_merge))
                    current_node = tgt

                elif k == "true_body_last":
                    if node_pair_stack:
                        if node_pair_stack[-1].end is None:
                            node_pair_stack[-1].end = tgt
                    current_node = tgt

                elif k == "false_body_start":
                    if node_pair_stack:
                        p = node_pair_stack.pop()
                        if p.end is None:
                            p.end = tr.get("target_index")  # best effort
                        pending_else = p
                    current_node = tgt

                elif k == "false_body_last":
                    pending_else = None
                    current_node = tgt

                elif k == "false_body_absent":
                    if node_pair_stack:
                        p = node_pair_stack.pop()
                        if p.end is None:
                            p.end = tgt
                    current_node = tgt

                elif k == "transfer_fail":
                    last_transfer_fail_edge = (src, tgt)
                    current_node = tgt

                elif k in {"efsm_fail", "function_fail"}:
                    last_transfer_fail_edge = None
                    current_node = tgt

                else:
                    # normal sequential: treat target as next current location
                    current_node = tgt

                # no overriding of last-to-S0 when locked
            else:
                src = None
                tgt = None

                # USER INVOCATION
                if k == "user_invocation":
                    invocation_node = _ensure_user_invocation_node()
                    src = INITIAL_NODE
                    tgt = invocation_node
                    if current_node == INITIAL_NODE:
                        current_node = invocation_node

                # IF/ELSE stack
                elif k == "true_body_start":
                    inherited_merge = None
                    if prev_k == "false_body_start" and pending_else is not None:
                        inherited_merge = _ensure_end(pending_else)
                        pending_else = None

                    node_pair_stack.append(NodePair(start=current_node, end=inherited_merge))
                    src = current_node
                    tgt = get_new_node("target")
                    current_node = tgt

                elif k == "true_body_last":
                    if not node_pair_stack:
                        node_pair_stack.append(NodePair(start=current_node, end=get_new_node("target")))

                    top = node_pair_stack[-1]
                    merge = _ensure_end(top)
                    src = current_node
                    tgt = merge
                    current_node = tgt

                elif k == "false_body_start":
                    if not node_pair_stack:
                        raise RuntimeError("false_body_start encountered but node_pair_stack is empty.")
                    p = node_pair_stack.pop()
                    _ensure_end(p)
                    pending_else = p
                    src = p.start
                    tgt = get_new_node("target")
                    current_node = tgt

                elif k == "false_body_last":
                    if pending_else is None:
                        raise RuntimeError("false_body_last encountered but pending_else is None.")
                    merge = _ensure_end(pending_else)
                    src = current_node
                    tgt = merge
                    current_node = tgt
                    pending_else = None

                elif k == "false_body_absent":
                    if not node_pair_stack:
                        raise RuntimeError("false_body_absent encountered but node_pair_stack is empty.")
                    p = node_pair_stack.pop()
                    merge = _ensure_end(p)
                    src, tgt = p.start, merge
                    current_node = tgt

                # TRANSFER FAIL chain
                elif k == "transfer_fail":
                    src = current_node
                    tgt = get_new_node("target")
                    last_transfer_fail_edge = (src, tgt)
                    current_node = tgt

                elif k in {"efsm_fail", "function_fail"}:
                    if last_transfer_fail_edge is not None:
                        _, fail_tgt = last_transfer_fail_edge
                        src = fail_tgt
                        tgt = INITIAL_NODE
                        current_node = tgt
                        last_transfer_fail_edge = None
                    else:
                        src = current_node
                        tgt = INITIAL_NODE
                        current_node = tgt

                # other specials (kept conservative)
                elif k == "first_transition":
                    src = INITIAL_NODE
                    tgt = get_new_node("target")
                    current_node = tgt

                elif k == "transfer_success":
                    src = get_new_node("source_reduced")
                    tgt = get_new_node("target")
                    current_node = tgt

                elif k == "sender_transfer_initial":
                    src = current_node
                    sender_transfer_node = src
                    tgt = get_new_node("target")
                    transfer_success_source_node = tgt
                    current_node = tgt

                elif k == "sender_transfer":
                    src = sender_transfer_node if sender_transfer_node else current_node
                    tgt = get_new_node("target")
                    transfer_success_source_node = tgt
                    current_node = tgt

                elif k == "sender_transfer_success_initial":
                    src = transfer_success_source_node if transfer_success_source_node else current_node
                    tgt = get_new_node("target")
                    sender_transfer_merge_node = tgt
                    temporary_source_node = tgt
                    current_node = tgt

                elif k == "sender_transfer_success":
                    src = transfer_success_source_node if transfer_success_source_node else current_node
                    tgt = sender_transfer_merge_node if sender_transfer_merge_node else get_new_node("target")
                    current_node = tgt

                elif k == "require_true":
                    src = current_node
                    require_node = src
                    tgt = get_new_node("target")
                    current_node = tgt

                elif k == "require_false":
                    src = require_node if require_node else current_node
                    tgt = INITIAL_NODE
                    current_node = tgt

                # default sequential
                else:
                    if temporary_source_node:
                        src = temporary_source_node
                        temporary_source_node = ""
                    else:
                        src = current_node

                    if k == "self_loop":
                        tgt = src
                    else:
                        tgt = tr.get("target_index") or get_new_node("target")

                    current_node = tgt

                # Force last transition to S0 ONLY when not locked
                if i == n_transitions - 1:
                    tgt = INITIAL_NODE
                    current_node = INITIAL_NODE

                tr["source_index"] = src
                tr["target_index"] = tgt

            # collect nodes
            add_node_to_efsm_node_list(tr["source_index"], tr["target_index"])

            # events (independent of locking)
            if not tr.get("events"):
                if i == 0:
                    event_name = str(efsm + "1")
                elif i == n_transitions - 1:
                    event_name = str(efsm + "X")
                else:
                    event_name = str(efsm + str(i + 1))
                tr["event"] = event_name
                add_events_to_xml(event_name)
            else:
                for event_name in tr["events"]:
                    add_events_to_xml(event_name)

            ordered_transitions.append(tr)
            prev_k = k

        # Merge-fix (only modify non-locked transitions)
        if ordered_transitions:
            last_tr = ordered_transitions[-1]
            last_k = _normalize_if_markers(ttype(last_tr))

            if last_k in {"false_body_last", "false_body_absent"}:
                old_merge = None
                for j in range(len(ordered_transitions) - 2, -1, -1):
                    tj = ordered_transitions[j]
                    kj = _normalize_if_markers(ttype(tj))
                    if kj in {"true_body_last", "false_body_last", "false_body_absent"}:
                        cand = tj.get("target_index")
                        if cand and cand != INITIAL_NODE:
                            old_merge = cand
                            break

                if old_merge:
                    for t in ordered_transitions:
                        if id(t) in locked_ids:
                            continue
                        if t.get("target_index") == old_merge:
                            t["target_index"] = INITIAL_NODE

        # build xml
        for tr in ordered_transitions:
            EdgeList.append(add_transition_to_xml(tr))

    pre_supremica["Components"][efsm]["edge_list"] = EdgeList
    pre_supremica["Components"][efsm]["node_list"] = add_nodes_to_xml(efsm_node_list)

pre_supremica["Events"] = EventDeclList
