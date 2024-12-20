def get_escapes(dataset_name):
    map_dict = {
        'airbnb-simplified_subsampled': {
            'datetime': [("users","date_first_booking"), ("users","date_account_created"), ("users","timestamp_first_active")]
        },
        "rossmann_subsampled": {
            "datetime": [("historical","Date")]
        },
        "walmart_subsampled": {
            "datetime": [("features","Date"), ("depts","Date")]
        }
    }
    
    ret = map_dict[dataset_name] if dataset_name in map_dict else {}
    ret.setdefault('id', [])
    ret.setdefault('time', [])
    ret.setdefault('datetime', [])
    return ret
