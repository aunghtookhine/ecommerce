def dict_strip(dict):
    for key in dict:
        if type(dict[key]) == str:
            dict[key] = dict[key].strip()
