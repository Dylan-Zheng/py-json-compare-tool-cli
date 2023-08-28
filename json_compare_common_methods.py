from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import clear

import difflib
import re

def is_blank(value):
    if value is None or value.strip() != "":
        return True
    else:
        return False

def list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


def get_last_special_char_index(text):
    for index, char in enumerate(reversed(text)):
        if not char.isalnum():
            return len(text) - index - 1
    return -1


def get_last_word(text):
    index = get_last_special_char_index(text)
    if index + 1 < len(text):
        return text[index + 1:]
    return ""


class CustomWordCompleter(Completer):
    def __init__(self, words):
        self.words = words

    def find_five_best_non_perfect_matches(self, target_path):
        best_matches = []
        template_paths = self.words
        match_count = 5

        for template_path in template_paths:
            similarity = difflib.SequenceMatcher(None, target_path, template_path).ratio()

            if similarity < 1.1:  # Only consider non-perfect matches
                if len(best_matches) < match_count:
                    best_matches.append((template_path, similarity))
                    best_matches.sort(key=lambda x: x[1], reverse=True)
                else:
                    if similarity > best_matches[-1][1]:
                        best_matches.pop()
                        best_matches.append((template_path, similarity))
                        best_matches.sort(key=lambda x: x[1], reverse=True)

        return [match[0] for match in best_matches]

    def get_completions(self, document, complete_event):
        word = get_last_word(document.text_before_cursor)
        matches = self.find_five_best_non_perfect_matches(word)
        for match in matches:
            yield Completion(match, start_position=-len(word))


class CustomCompleter(Completer):
    def __init__(self, words):
        self.words = words

    def find_five_best_non_perfect_matches(self, target_path):
        best_matches = []
        template_paths = self.words
        match_count = 5

        for template_path in template_paths:
            similarity = difflib.SequenceMatcher(None, target_path, template_path).ratio()

            if similarity < 1.1:  # Only consider non-perfect matches
                if len(best_matches) < match_count:
                    best_matches.append((template_path, similarity))
                    best_matches.sort(key=lambda x: x[1], reverse=True)
                else:
                    if similarity > best_matches[-1][1]:
                        best_matches.pop()
                        best_matches.append((template_path, similarity))
                        best_matches.sort(key=lambda x: x[1], reverse=True)

        return [match[0] for match in best_matches]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        matches = self.find_five_best_non_perfect_matches(text_before_cursor)
        for match in matches:
            yield Completion(match, start_position=-len(text_before_cursor))


def json_to_schema(json_obj, nested_list=False):
    if isinstance(json_obj, dict):
        schema = {}
        for key, value in json_obj.items():
            schema[key] = json_to_schema(value, nested_list)
        return schema
    elif isinstance(json_obj, list):
        return [json_to_schema(json_obj[0], True)]
    else:
        return get_data_type(json_obj)


def get_data_type(data):
    if isinstance(data, bool):
        return "boolean"
    elif isinstance(data, int):
        return "integer"
    elif isinstance(data, float):
        return "float"
    elif isinstance(data, str):
        return "string"
    else:
        return "unknown"


def list_all_paths(data, parent_path="", separator="."):
    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{parent_path}{separator}{key}" if parent_path else key
            paths.append(new_path)
            paths.extend(list_all_paths(value, new_path, separator))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            new_path = f"{parent_path}[]"
            paths.append(new_path)
            paths.extend(list_all_paths(value, new_path, separator))

    return paths


def create_mapping_template(json_a_paths, json_b_paths, mapping_template={}):
    copied_json_a_paths = json_a_paths[:]
    copied_json_b_paths = json_b_paths[:]
    copied_json_a_paths.extend([";p", ";n", ";q", ';d', ";j"])
    copied_json_b_paths.extend([";p", ";n", ";q", ';d', ";j"])

    json_a_path_completer = CustomCompleter(copied_json_a_paths)
    json_b_path_completer = CustomCompleter(copied_json_b_paths)

    prev_index = 0
    index = 0
    max_len = len(json_a_paths)

    while index < max_len:
        exist_mapping = mapping_template.get(json_a_paths[index])
        clear()
        msg = "END MODIFY" if index >= max_len - 1 else "next"
        print(f"Path {index + 1}/{max_len}"
              f"\nType: \";p\" previous, "
              f"\";n\" {msg}, "
              f"\";d\" delete current path, "
              f"\";j#\" jump to path number, "
              f"\";q\" exit")
        if exist_mapping:
            print(f"If below pair are correct, tppe \";n\" to next."
                  f"\nEXP: {json_a_paths[index]}"
                  f"\nDPS: {exist_mapping}"
                  f"\nYou can also enter the another path in DSP and Press \"ENTER\" key to confirm modify:")
        else:
            print(f"Enter the corresponding path in DPS for EXP: '{json_a_paths[index]}':")
        action = None

        # 创建键绑定
        kb = KeyBindings()

        path_b = ""

        @kb.add("enter")
        def _(event):
            nonlocal index
            nonlocal action
            action = "enter"
            if len(event.current_buffer.text) > 0 and event.current_buffer.text[0] != ";":
                index = index + 1
            event.app.exit(result=event.current_buffer.text)

        result = prompt("", completer=json_b_path_completer, key_bindings=kb)

        if result == ";p":
            action = "left"
            if index > 0:
                index = index - 1
            if exist_mapping:
                path_b = exist_mapping
            else:
                path_b = None
        elif result == ";n":
            action = "right"
            index = index + 1
            if exist_mapping:
                path_b = exist_mapping
            else:
                path_b = None
        elif result == ";d":
            action = "delete"
            index = index
            path_b = None
        elif result.startswith(";j"):
            action = "jump"
            jump_index = int(re.search(r'\d+', result).group())
            index = jump_index if jump_index < max_len else max_len - 1
            if exist_mapping:
                path_b = exist_mapping
            else:
                path_b = None
        elif result == ";q":
            break
        else:
            path_b = result

        correct_index = index - 1
        if action == "left":
            correct_index = index + 1

        if action == "enter":
            a_dim = len(find_all_square_brackets_indices(json_a_paths[correct_index]))
            b_dim = len(find_all_square_brackets_indices(path_b))
            if a_dim != b_dim:
                create_manual_list_mapping(json_a_paths[correct_index], path_b, json_a_path_completer,
                                           json_b_path_completer, mapping_template)
            else:
                mapping_template[json_a_paths[correct_index]] = path_b
        elif action == "delete":
            mapping_template[json_a_paths[index]] = path_b
        else:
            mapping_template[json_a_paths[correct_index]] = path_b

        if (action == "right" or action == "enter") and index >= max_len:
            print(f"Do you want to end modify mapping template(Y/N)?")
            user_input = input()
            if user_input == "Y" or user_input == "y":
                break
            elif user_input == "N" or user_input == "n":
                index = index - 1
    return mapping_template


def create_manual_list_mapping(json_a_path, json_b_path, json_a_path_completer, json_b_path_completer,
                               mapping_template={}):
    index = 0
    tmp_mapping_list = []

    def command(result):
        nonlocal index
        nonlocal tmp_mapping_list
        action = "enter"
        if result == ";p":
            action = "left"
            if index > 0:
                index = index - 1
        elif result == ";n":
            action = "right"
            if index < len(tmp_mapping_list):
                index = index + 1
        elif result == ";d":
            action = "delete"
            index = index
            tmp_mapping_list.pop(index)
        elif result.startswith(";j"):
            action = "jump"
            jump_index = int(re.search(r'\d+', result).group())
            index = jump_index if jump_index < max_len else max_len - 1
        elif result == ";q":
            action = "exit"
        else:
            action = "enter"
        return (action, result)

    while True:
        clear()
        exp_path = json_a_path.replace("[]", "[?]") if index >= len(tmp_mapping_list) else tmp_mapping_list[index][0]
        dps_path = json_b_path.replace("[]", "[?]") if index >= len(tmp_mapping_list) else tmp_mapping_list[index][1]

        p_msg = "previous" if index >= 0 else "no action"
        n_msg = "next" if index < len(tmp_mapping_list) - 1 else "no action"
        print(f"Path {index + 1}/{len(tmp_mapping_list)}"
              f"\nType: \";p\" {p_msg}, \";n\" {n_msg}, \";q\"  exit")
        print(f"You are in manually list mapping mode, it happened when EXP and DPS path have different size of "
              f"dimension "
              f"\nEXP: {exp_path}"
              f"\nDPS: {dps_path}"
              f"\nEnter EXP path and give appropriate indices")
        result = prompt("", completer=json_a_path_completer)
        ret = command(result)
        a_path = ""
        if ret[0] == "enter":
            a_path = ret[1]
        elif ret[0] == "exit":
            break;
        else:
            continue

        print(f"\nEnter DPS path and give appropriate indices")
        result = prompt("", completer=json_b_path_completer)
        ret = command(result)
        b_path = ""
        if ret[0] == "enter":
            b_path = ret[1]
        elif ret[0] == "exit":
            break;
        else:
            continue

        if index >= len(tmp_mapping_list):
            tmp_mapping_list.append((a_path, b_path))
        else:
            tmp_mapping_list[index] = (a_path, b_path)
        index = index + 1

    for item in tmp_mapping_list:
        mapping_template[item[0]] = item[1]
    return mapping_template


def create_array_sorting_rules(paths, json, arr_soring_rules={}):
    index = 0
    arr_paths = list(filter(lambda path: path.endswith("[]"), paths))
    max_len = len(arr_paths)
    keys = get_all_keys(json)
    completer = CustomWordCompleter(keys)

    for path in arr_paths:
        if not arr_soring_rules.get(path):
            arr_soring_rules[path] = {}
            arr_soring_rules[path]["rules"] = None
            arr_soring_rules[path]["priority"] = 0

    def command(prompt_result):
        nonlocal max_len
        nonlocal index
        nonlocal arr_paths
        nonlocal arr_soring_rules

        action = "enter"
        if prompt_result == ";p":
            action = "left"
            if index > 0:
                index = index - 1
        elif prompt_result == ";n":
            action = "right"
            if index < len(arr_paths):
                index = index + 1
        elif prompt_result == ";d":
            action = "delete"
            index = index
            arr_soring_rules[arr_paths[index]] = {}
            arr_soring_rules[arr_paths[index]]["rules"] = None
            arr_soring_rules[arr_paths[index]]["priority"] = 0
        elif prompt_result.startswith(";j"):
            action = "jump"
            jump_index = int(re.search(r'\d+', prompt_result).group())
            index = jump_index if jump_index < max_len else max_len - 1
        elif prompt_result == ";q":
            action = "exit"
        else:
            action = "enter"

        return action, prompt_result

    curr_index = 0
    while index < max_len:
        curr_index = index
        clear()

        p_msg = "previous" if index >= 0 else "no action"
        n_msg = "next" if index < len(paths) - 1 else "no action"
        print(f"Path {index + 1}/{len(paths)}"
              f"\nType: \";p\" {p_msg}, \";n\" {n_msg}, \";q\"  exit"
              f"\nProvide sorting rule for array: {arr_paths[index]}"
              f"\nEnter lamdba: ")
        result = prompt("", completer=completer)
        ret = command(result)
        if ret[0] == "enter":
            lambda_str = ret[1]
        elif ret[0] == "exit":
            break
        else:
            continue

        print(f"\nEnter priority: ")
        result = prompt("")
        ret = command(result)
        if ret[0] == "enter":
            priority = ret[1]
            index = index + 1
        elif ret[0] == "exit":
            break
        else:
            continue

        print(f"{lambda_str} {priority}")
        arr_soring_rules[arr_paths[curr_index]] = {}
        arr_soring_rules[arr_paths[curr_index]]["rules"] = lambda_str
        arr_soring_rules[arr_paths[curr_index]]["priority"] = priority

    return arr_soring_rules


def find_dps_valuey_path(json, path):
    pos_list = find_all_square_brackets_indices(path)

    prev_end_pos = 0
    new_path = ""
    for pos in pos_list:
        new_path = new_path + path[prev_end_pos:pos] + ".[]"
        prev_end_pos = pos + 2

    keys = new_path.split('.')
    result_json = json
    for key in keys:
        if key == "[]":
            tmp_json = result_json[0]
        else:
            tmp_json = result_json.get(key)
    return result_json


def get_all_keys(input_obj, prefix=""):
    keys = set()

    if isinstance(input_obj, dict):
        for key, value in input_obj.items():
            full_key = f"{prefix}{key}"
            keys.add(key)
            keys.update(get_all_keys(value, f"{full_key}."))
    elif isinstance(input_obj, list):
        for idx, item in enumerate(input_obj):
            keys.update(get_all_keys(item, f"{prefix}{idx}."))

    return list(keys)


def extract_paths_values(data, path="", path_value_dict=None):
    if path_value_dict is None:
        path_value_dict = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            extract_paths_values(value, new_path, path_value_dict)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            extract_paths_values(item, new_path, path_value_dict)
    else:
        path_value_dict[path] = data

    return path_value_dict


def find_best_match(target_path, src_paths):
    best_match = None
    best_similarity = 0

    for path in src_paths:
        similarity = difflib.SequenceMatcher(None, target_path, path).ratio()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = path

    return best_match


def auto_mapping(target_paths, src_paths, mapping_template):
    mapping = {}
    for target_path in target_paths:
        if is_blank(mapping_template.get(target_path, None)):
            best_match = find_best_match(target_path, src_paths);
            mapping[target_path] = best_match
    return mapping


def find_all_square_brackets_indices(path):
    square_indices = []
    target = "[]"
    index = path.find(target)
    while index != -1:
        square_indices.append(index)
        index = path.find(target, index + 1)
    return square_indices


def map_b_paths_to_a(mapping_template, b_path_value_dict):
    b_stdzng_path_value_dict = {}

    for b_path, b_value in b_path_value_dict.items():
        best_match = find_best_match(b_path, mapping_template.values())

        if best_match:
            a_path_template = next(
                a_key for a_key, b_path_temp in mapping_template.items() if b_path_temp == best_match)
            new_path = a_path_template
            b_indices_str = re.findall(r'\[(\d+)\]', b_path)
            if len(b_indices_str) > 0:
                square_indices = find_all_square_brackets_indices(a_path_template)
                index = 0
                prev_end_pos = 0
                new_path = ""
                for pos in square_indices:
                    new_path = new_path + a_path_template[prev_end_pos:pos + 1] + b_indices_str[index] + "]"
                    prev_end_pos = pos + 2
                    index = index + 1
                if prev_end_pos < len(a_path_template):
                    new_path = new_path + a_path_template[prev_end_pos:]
        b_stdzng_path_value_dict[new_path] = b_value
    return b_stdzng_path_value_dict


def compare_dicts(dict_a, dict_b):
    diff_list = []

    for path, exp_value in dict_a.items():
        dps_value = dict_b.get(path)
        is_match = exp_value == dps_value
        diff_list.append({
            "path": path,
            "exp_value": exp_value,
            "dps_value": dps_value,
            "isMatch": is_match
        })

    # Check for paths in dict_b that are not in dict_a
    for path, dps_value in dict_b.items():
        if path not in dict_a:
            diff_list.append({
                "path": path,
                "exp_value": "path no found",
                "dps_value": "path no found",
                "isMatch": False
            })

    return diff_list


def print_compare_dicts_result(dict_a, dict_b):
    print("{:<30} {:<20} {:<20}".format("Path", "Value in A", "Value in B"))
    print("=" * 70)

    for path, exp_value in dict_a.items():
        dps_value = dict_b.get(path)

        if dps_value is None:
            dps_value = "N/A"

        print("{:<30} {:<20} {:<20}".format(path, exp_value, dps_value))
        print("-" * 70)

        if exp_value == dps_value:
            print("Values match.")
        else:
            print("Values do not match.")

        print("=" * 70)

    # Check for paths in dict_b that are not in dict_a
    for path, dps_value in dict_b.items():
        if path not in dict_a:
            exp_value = "N/A"
            print("{:<30} {:<20} {:<20}".format(path, exp_value, dps_value))
            print("-" * 70)
            print("Values do not match.")
            print("=" * 70)
