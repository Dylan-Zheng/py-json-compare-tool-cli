# import json
# import openpyxl
# from openpyxl.styles import PatternFill, Alignment
# from openpyxl.utils import get_column_letter
#
# from json_compare_common_methods import *
#
# json_str_a = '''
# {
#     "a": "fsdf",
#     "b": {
#         "c": true,
#         "d": 1,
#         "e": [{"c": [1,2,3]}, {"c": [1,2,3]}, {"c": [1,3,4]}]
#     },
#     "f": [[1,2,3], [1,2,3], [1,2,3]],
#     "g": {"a": "1", "b": "2", "c": "3"}
# }
# '''
#
# json_str_b = '''
# {
#     "aa": "xyz",
#     "bb": {
#         "cc": false,
#         "dd": 2,
#         "ee": [{"ccc": [1,2]}, {"ccc": [1]}, {"ccc": [1]}]
#     },
#     "ff": [[1,2,3], [1,2,3], [1,2,3]],
#     "gg": [1,2,3]
# }
# '''
#
# json_a = json.loads(json_str_a)
# json_b = json.loads(json_str_b)
#
# schema_a = json_to_schema(json_a)
# schema_b = json_to_schema(json_b)
#
# print(schema_a)
# print(schema_b)
#
# json_a_paths = list_all_paths(schema_a)
# json_b_paths = list_all_paths(schema_b)
#
# print(json_a_paths)
# print(json_b_paths)
#
# # sorting_rules = create_array_sorting_rules(json_a_paths, schema_a)
# # formatted_output = json.dumps(sorting_rules, indent=100)
# # print(sorting_rules)
#
# mapping_template = auto_mapping(json_a_paths, json_b_paths, {})
#
# # mapping_template = create_mapping_template(json_a_paths, json_b_paths, mapping_template)
#
# print("\nMapping Template:")
# for path_a, path_b in mapping_template.items():
#     print(f"{path_a} -> {path_b}")
#
# a_path_value_dict = extract_paths_values(json_a)
# b_path_value_dict = extract_paths_values(json_b)
#
# b_stdzng_path_value_dict_out = map_b_paths_to_a(mapping_template, b_path_value_dict)
#
# print("\nA Path and Value Dictionary:")
# for path, value in a_path_value_dict.items():
#     print(f"{path} -> {value}")
#
# print("\nB Path and Value Dictionary:")
# for path, value in b_path_value_dict.items():
#     print(f"{path} -> {value}")
#
# print("\nB Standardized Path Value Dictionary:")
# for path, value in b_stdzng_path_value_dict_out.items():
#     print(f"{path} -> {value}")
#
# diff_result = compare_dicts(b_stdzng_path_value_dict_out, a_path_value_dict)
#
# ##################################################
#
# workbook = openpyxl.Workbook()
# sheet = workbook.active
#
# sheet.append(["Path", "EXP Value", "DPS Value", "Is Match"])
#
# fill_not_match = PatternFill(start_color="FFCCFF", end_color="FFCCFF", fill_type="solid")
#
# for diff_item in diff_result:
#     row = [diff_item["path"], diff_item["exp_value"], diff_item["dps_value"], diff_item["isMatch"]]
#     sheet.append(row)
#
#     if not diff_item["isMatch"]:
#         sheet[sheet.max_row][-1].fill = fill_not_match
#
#     for col_idx in [2, 3]:  # "Value in A" is at column index 2, "Value in B" is at column index 3
#         cell = sheet.cell(row=sheet.max_row, column=col_idx)
#         cell.alignment = Alignment(horizontal="right")
#
# for column in sheet.columns:
#     max_length = 0
#     column = [cell for cell in column]
#     for cell in column:
#         try:
#             if len(str(cell.value)) > max_length:
#                 max_length = len(cell.value)
#         except:
#             pass
#     adjusted_width = (max_length + 2) * 1.2  # Adjust width slightly for better visibility
#     sheet.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width
#
# # 保存Excel文件
# excel_file_path = "comparison_result.xlsx"
# workbook.save(excel_file_path)
