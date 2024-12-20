from er import generate_er_graph
from dataset_info import get_escapes
from testcode import Xargs

def set_relation_item(item, pk, ck, pn, cn):
    item["parent_primary_key"] = pk
    item["child_foreign_key"] = ck
    item["parent_table_name"] = pn
    item["child_table_name"] = cn

def get_relation_item(item):
    pk = item["parent_primary_key"]
    ck = item["child_foreign_key"]
    pn = item["parent_table_name"]
    cn = item["child_table_name"]
    return pk, ck, pn, cn

def generate_xargs(metadata, dataset_name, logger):
    generate_er_graph(metadata.relationships, dataset_name)

    table_names_mapper = {}
    table_columns_using = {}
    # 处理更名！########################
    for item in metadata.relationships:
        pk, ck, pn, cn = get_relation_item(item)
        # 为了防止参考键名称不同，需要更名！
        if (pn, pk) not in table_columns_using:
            table_columns_using[(pn, pk)] = []
        table_columns_using[(pn, pk)].append((cn, ck))
    
    # 生成更名map
    for (pn, pk), usings in table_columns_using.items():
        newpk = f"{pn}-{pk}"
        for (cn, ck) in usings:
            if cn not in table_names_mapper:
                table_names_mapper[cn] = {}
            table_names_mapper[cn][ck] = newpk
        if pn not in table_names_mapper:
            table_names_mapper[pn] = {}
        table_names_mapper[pn][pk] = newpk

    print(table_names_mapper)
    
    # # 处理metadata（更名）
    # for item in metadata.relationships:
    #     pk, ck, pn, cn = get_relation_item(item)
    #     pk = table_names_mapper[pn][pk]
    #     ck = table_names_mapper[cn][ck]
    #     set_relation_item(item, pk, ck, pn, cn)
    
    # 处理关系 ##############
    
    x_table = []
    x_key_p2c_map = {}
    x_key_c2p_map = {}
    
    for item in metadata.relationships:
        pk, ck, pn, cn = get_relation_item(item)
        
        if pn not in x_table:
            x_table.append(pn)
            x_key_p2c_map[pn] = {}
            x_key_c2p_map[pn] = {}
        if cn not in x_table:
            x_table.append(cn)
            x_key_p2c_map[cn] = {}
            x_key_c2p_map[cn] = {}
        # 以下的两个warn是等价的。
        if ck not in [v[1] for v in x_key_p2c_map[pn].values()]:
            x_key_p2c_map[pn][pk] = (cn, ck)
        else:
            logger.warning(f"{(pn,pk)} <= {cn,ck} 被忽略了，因为不支持单表中对同一个外键的多次参考（有2个列参照同1个列），已有参照 {(pn,pk)} <= {x_key_p2c_map[pn][pk]}")
            # 删除更名
            del table_names_mapper[cn][ck]
            continue
        if pn not in x_key_c2p_map[cn]:
            x_key_c2p_map[cn][pn] = (pk, ck)
        else:
            logger.warning(f"{(pn,pk)} <= {cn,ck} 被忽略了，因为不支持单表中对同一个表有多个外键参考（有多个列参照同一个表的键），已有参照 {(pn,pk)} <= {cn, x_key_c2p_map[cn][pn][1]}")
            del table_names_mapper[cn][ck]
            continue

            

    print(x_key_c2p_map)
    print("============")
    print(x_key_p2c_map)
    print("============")
    x_key = []
    parent_subset = set()
    for tb in x_table:
        if len(parent_subset) > 0:
            rela = {}
            keys = set()
            for ptb in parent_subset: # 查找当前结点有无孩子已经被连接。
                rela[ptb] = x_key_p2c_map[ptb]
                for v in rela[ptb].values():
                    if v[0] == tb:
                        keys.add(table_names_mapper[tb][v[1]])
            
            for ptb, v in x_key_p2c_map[tb].values():
                if ptb in parent_subset:
                    keys.add(table_names_mapper[ptb][v])
            
            parents_key = []
            for ptb in parent_subset: # 对父亲考虑,查找是否父亲已经被连接了。
                if ptb in x_key_c2p_map[tb]:
                    tk = x_key_c2p_map[tb][ptb][1]
                    tk = table_names_mapper[tb][tk]
                    parents_key.append(tk)
            
            keys = keys.union(parents_key)
            print(tb, keys, rela, parents_key)
            
            # set(item for item in rela.values())
            x_key.append(keys)
        parent_subset.add(tb)
        # x_key.append() [ x_key_map[tbn].values() for i,tbn in enumerate(x_table) if i>0]
    print(x_key)

    if input("Check:")!='':
        exit(1)
        
    


    escapes = get_escapes(dataset_name)

    x_args = Xargs.XArg(
        x_table=x_table,
        x_key=x_key,
        x_how=['outer']*len(x_key),
        meta_id_escapes=escapes['id'],
        meta_time_escapes=escapes['time'],
        meta_datetime_escapes=escapes['datetime']
    )
    return table_names_mapper, x_args