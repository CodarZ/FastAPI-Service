#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Sequence

from backend.common.enum.custom import BuildTreeEnum
from backend.utils.serializers import RowData, select_list_serialize


def get_tree_nodes(rows: Sequence[RowData]):
    """将原始行数据序列化为树形结构的节点列表"""
    nodes = select_list_serialize(rows)
    nodes.sort(key=lambda x: x['id'])
    return nodes


def traversal_to_tree(nodes: list[dict[str, Any]]):
    """遍历 构造树形结构"""
    tree: list[dict[str, Any]] = []
    node_dict = {node['id']: node for node in nodes}

    for node in nodes:
        parent_id = node.get('parent_id')
        if parent_id is not None and parent_id in node_dict:
            parent_node = node_dict[parent_id]
            parent_node.setdefault('children', []).append(node)
        else:
            tree.append(node)
    return tree


def recursive_to_tree(nodes: list[dict[str, Any]], *, parent_id: int | str | None = None):
    """递归 构造树形结构"""
    tree: list[dict[str, Any]] = []
    for node in nodes:
        if node.get('parent_id') == parent_id:
            children = recursive_to_tree(nodes, parent_id=node['id'])
            if children:
                node.setdefault('children', []).append(children)
            tree.append(node)
    return tree


def get_tree_data(
    rows: Sequence[RowData],
    type: BuildTreeEnum = BuildTreeEnum.traversal,
    *,
    parent_id: int | str | None = None,
):
    """将原始数据行序列变为树形结构"""

    nodes = get_tree_nodes(rows)
    match type:
        case BuildTreeEnum.traversal:
            return traversal_to_tree(nodes)
        case BuildTreeEnum.recursive:
            return recursive_to_tree(nodes, parent_id=parent_id)
        case _:
            raise ValueError(f'无效的算法类型: {type}')
