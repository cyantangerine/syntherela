from er import generate_er_graph
from dataset_info import get_escapes
from testcode import Xargs
class N2NError(Exception):
    pass
class N2NMap:
    def __init__(self, tbnames):
        self.pks: dict[str, set[str]] = {tn2: set() for tn2 in tbnames}
        # cn -> pn: (pk, ck)
        self.ref_to: dict[str, dict[str, set[tuple[str, str]]]] = {}
        # pn -> cn: [(pk, ck)]
        self.ref_from: dict[str, dict[str, set[tuple[str, str]]]] = {}
        for tn in tbnames:
            self.ref_to[tn] = {tn2: set() for tn2 in tbnames}
            self.ref_from[tn] = {tn2: set() for tn2 in tbnames}
        
    def set_relation(self, pn, cn, pk, ck):
        if self.ref_to[pn][cn]:
            raise N2NError("不能形成环路")
        if pk in [v[0] for v in self.ref_from[pn][cn]]:
            raise N2NError("在单表中不能引用同一个pk两次")
        self.pks[pn].add(pk)
        if len(self.pks[pn]) > 1:
            print(f"侦测到{pn}具有复合主键{self.pks[pn]}")
        self.ref_to[cn][pn].add((pk, ck))
        self.ref_from[pn][cn].add((pk, ck))
    
    def get_node(self, node) -> tuple[dict[str,set[tuple[str, str]]], dict[str,set[tuple[str, str]]]]:
        return self.ref_from[node], self.ref_to[node]
        
        
    def get_relation(self, pn, cn) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
        return self.ref_from[pn][cn], self.ref_to[cn][pn]

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
    x_table = []
    for item in metadata.relationships:
        pk, ck, pn, cn = get_relation_item(item)
        
        if pn not in x_table:
            x_table.append(pn)
        if cn not in x_table:
            x_table.append(cn)
        
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
    
    
    rela_map = N2NMap(x_table)
    # x_key_p2c_map = {}
    # x_key_c2p_map = {}
    
    for item in metadata.relationships:
        pk, ck, pn, cn = get_relation_item(item)
        try:
            rela_map.set_relation(pn, cn, pk, ck)
        except N2NError as e:
            rela_from, rela_to = rela_map.get_relation(pn,cn)
            logger.warning(f"{e} ERROR {(pn,pk)} <= {cn,ck} 被忽略了，已有参照: {pn} => {cn}: {rela_from}, {cn} => {pn}: {rela_to}")
            # 删除更名
            del table_names_mapper[cn][ck]
            continue
        # if pn not in x_key_c2p_map[cn]:
        #     x_key_c2p_map[cn][pn] = (pk, ck)
        # else:
        #     raise ValueError
        #     logger.warning(f"ERROR BBBBB {(pn,pk)} <= {cn,ck} 被忽略了，因为不支持单表中对同一个表有多个外键参考（有多个列参照同一个表的键），已有参照 {(pn,pk)} <= {cn, x_key_c2p_map[cn][pn][1]}")
        #     del table_names_mapper[cn][ck]
        #     continue

            
    for tb in x_table:
        f, t = rela_map.get_node(tb)
        for ff in [f, t]:
            ks = list(ff.keys())
            for k in ks:
                if not ff[k]:
                    del ff[k]
        print(f"{tb}: 被参考 {f}，参考了 {t}")
    # print(x_key_c2p_map)
    # print("============")
    # print(x_key_p2c_map)
    # print("============")
    x_key = []
    parent_subset = set()
    for tb in x_table:
        if len(parent_subset) > 0:
            rf, rt = rela_map.get_node(tb)
            rela: dict[str, set] = {}
            keys = set()
            for k in rf:
                if k in parent_subset:
                    rela[k] = rf[k].copy()
            for k in rt:
                if k not in parent_subset:
                    continue
                if k in rela:
                    t = rt[k].copy()
                    rela[k] = t.union(rela[k])
                else:
                    rela[k] = rt[k]
            for pn, s in rela.items():
                for (pk, ck) in s:
                    keys.add(table_names_mapper[tb][ck])
            print(tb, keys, rela)
            x_key.append(keys)
        parent_subset.add(tb)
    print(x_key)

    # if input("Check:")!='':
    #     exit(1)
        
    


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

if __name__ == "__main__":
    import logging
    class m:
        relationships = [{
            "parent_table_name": "molecule",
            "parent_primary_key": "molecule_id",
            "child_table_name": "atom",
            "child_foreign_key": "molecule_id"
        },
        {
            "parent_table_name": "atom",
            "parent_primary_key": "atom_id",
            "child_table_name": "bond",
            "child_foreign_key": "atom_id"
        },
        {
            "parent_table_name": "atom",
            "parent_primary_key": "atom_id",
            "child_table_name": "bond",
            "child_foreign_key": "atom_id2"
        },
        {
            "parent_table_name": "atom",
            "parent_primary_key": "atom_id",
            "child_table_name": "gmember",
            "child_foreign_key": "atom_id"
        },
        {
            "parent_table_name": "group",
            "parent_primary_key": "group_id",
            "child_table_name": "gmember",
            "child_foreign_key": "group_id"
        }]
    meta = m()
    import sys
    logger = logging.getLogger(f"logger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    generate_xargs(meta, 'test', logger=logger)