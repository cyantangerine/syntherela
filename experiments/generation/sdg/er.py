from graphviz import Digraph

def generate_er_graph(table_relations):
    dot = Digraph(comment='ER Diagram')

    # 记录所有表
    tables = set()
    for relation in table_relations:
        tables.add(relation['parent_table_name'])
        tables.add(relation['child_table_name'])

    # 为每个表创建节点
    for table in tables:
        dot.node(table, table)

    # 为每个关系添加边
    for relation in table_relations:
        parent = relation['parent_table_name']
        child = relation['child_table_name']
        parent_key = relation['parent_primary_key']
        child_key = relation['child_foreign_key']
        
        # 在边上标注连接键
        dot.edge(parent, child, label=f'{parent_key} -> {child_key}')

    # 渲染 ER 图为文件或输出为 PNG
    dot.render('er_diagram', format='png', cleanup=True)
    return dot

if __name__ == "__main__":
    # 输入的关系数据
    table_relations = [
        {"parent_table_name": "molecule", "parent_primary_key": "molecule_id", "child_table_name": "atom", "child_foreign_key": "molecule_id"},
        {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "bond", "child_foreign_key": "atom_id"},
        {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "bond", "child_foreign_key": "atom_id2"},
        {"parent_table_name": "atom", "parent_primary_key": "atom_id", "child_table_name": "gmember", "child_foreign_key": "atom_id"},
        {"parent_table_name": "group", "parent_primary_key": "group_id", "child_table_name": "gmember", "child_foreign_key": "group_id"}
    ]
    # 生成 ER 图
    dot = generate_er_graph(table_relations)

    # 查看图形
    dot.view()  # 这会打开生成的 PNG 图像
