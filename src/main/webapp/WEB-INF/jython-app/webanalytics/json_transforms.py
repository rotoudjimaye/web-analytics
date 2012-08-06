# -*- coding: utf-8 -*-

import collections

from copy import deepcopy


def _get_deep_attr(obj, attr):
    for path in attr.split("."):
        try:
            obj = getattr(obj, path)
        except AttributeError: 
            return None
    return obj

def json_transform(obj, attrs_tree, extend=None):
    result = {}
    for attr in attrs_tree:
        _attr = attr.split("-")[0]
        val = attrs_tree[attr]
        
        if isinstance(val, dict): # val is a map
            objarray = getattr(obj, _attr)
            val = deepcopy(val)
            sort_key = val.pop("$_sort_key_$") if "$_sort_key_$" in val else None
            filter_funct = val.pop("$filter$") if "$filter$" in val else (lambda e: True)
            result[attr] = list()
            if sort_key:  
                objarray = sorted(objarray, key=sort_key)            
            for item in objarray:
                if filter_funct(item): result[attr].append(json_transform(item, attrs_tree=val))
                    
        elif isinstance(val, (list, tuple)): # val is list
            columns = val
            objarray = getattr(obj, _attr)
            
            result[attr] = {}
            result[attr]["$RECORDS$"] = []
            
            functs, formats, list_attrs, _columns = [], [], [], []
            for col in columns:                
                list_attrs.append(col["$attr"])
                formats.append(col["$format"] if "$format" in col else None)
                functs.append(col["$funct"] if "$funct" in col else None)
                _columns.append(dict([ (k, col[k]) for k in col if k != '$funct']))
                        
            for item in objarray:
                row = []
                for idx, col in enumerate(columns):
                    l_attr = list_attrs[idx]
                    funct = functs[idx]
                    fmat = formats[idx]
                    raw_value = _get_deep_attr(item, l_attr)
                    value = funct(raw_value) if (funct is not None) else (fmat % (raw_value,) if raw_value is not None else "") if (fmat is not None) else raw_value
                    row.append(value)
                result[attr]["$RECORDS$"].append(row)
    
            result[attr]["$COLUMNS$"] = _columns
        elif callable(val):
            funct = val
            field_value = funct( _get_deep_attr(obj, _attr) )
            result[attr] = field_value             
        else:
            fmat = attrs_tree[attr]
            field_value = _get_deep_attr(obj, _attr)
            result[attr] = field_value if fmat is None else (fmat %(field_value, ) if (field_value is not None) else None)
    if extend:
        result.update(extend)
    return result
