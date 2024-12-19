def dfs(table_relations, parent_table, visited, connection_order, connection_keys):
    visited.add(parent_table)
    
    # 查找所有与当前父表相关的子表
    for relation in table_relations:
        if relation["parent_table_name"] == parent_table and relation["child_table_name"] not in visited:
            child_table = relation["child_table_name"]
            foreign_key = relation["child_foreign_key"]
            primary_key = relation["parent_primary_key"]
            
            # 记录连接顺序和连接键
            connection_order.append(child_table)
            connection_keys.append([primary_key, foreign_key])
            
            # 递归调用 DFS，继续向下查找子表
            dfs(table_relations, child_table, visited, connection_order, connection_keys)

def generate_merge_order(table_relations):
    visited = set()
    connection_order = []
    connection_keys = []
    
    # 假设“molecule”表是根表（可以根据实际情况调整）
    root_table = "molecule"
    connection_order.append(root_table)
    
    # 开始深度优先搜索
    dfs(table_relations, root_table, visited, connection_order, connection_keys)
    
    return connection_order, connection_keys

# 输入的关系数据
table_relations = [
    {"parent_table_name": "molecule", "parent_primary_key": "molecule_id", "child_table_name": "atom", "child_foreign_key": "molecule_id"},
    {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "bond", "child_foreign_key": "atom_id"},
    {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "bond", "child_foreign_key": "atom_id2"},
    {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "gmember", "child_foreign_key": "atom_id"},
    {"parent_table_name": "group", "parent_primary_key": "group_id", "child_table_name": "gmember", "child_foreign_key": "group_id"}
]

# 生成连接顺序和连接键
connection_order, connection_keys = generate_merge_order(table_relations)

# 输出结果
print("连接顺序: ", connection_order)
print("连接键: ", connection_keys)
