def pprint_dict(d: dict, depth: int = 0) -> None:
    print("{")
    for k, v in d.items():
        print(f'{" " * (depth + 1) * 4}"{k}": ', end="")
        if isinstance(v, dict):
            depth += 1
            pprint_dict(v, depth)
            depth -= 1
        elif isinstance(v, list):
            depth += 1
            pprint_list(L=v, is_in_array=False, depth=depth)
            depth -= 1
        elif isinstance(v, str):
            print(f'"{v}",')
        else:
            print(f"{v},")
    print(" " * depth * 4, end="")
    if depth == 0:
        print("}")
    else:
        print("},")


def pprint_list(L: list, is_in_array: bool, depth: int = 0) -> None:
    if is_in_array:
        print(" " * depth * 4, end="")
    print("[")
    for elem in L:
        if isinstance(elem, dict):
            depth += 1
            pprint_dict(elem, depth)
            depth -= 1
        elif isinstance(elem, list):
            depth += 1
            pprint_list(L=elem, is_in_array=True, depth=depth)
            depth -= 1
        elif isinstance(elem, str):
            print(f'{" " * (depth + 1) * 4}"{elem}",')
        else:
            print(f'{" " * (depth + 1) * 4}{elem},')
    print(" " * depth * 4, end="")
    print("],")
