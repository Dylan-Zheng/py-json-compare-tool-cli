from json_compare_common_methods import *
import sys


class Commands:
    HELP = "help"
    CREATE_MAPPING_TEMPLATE = "create-mapping-template"
    CREATE_SORTING_RULES = "create-sorting-rules"
    COMPARE = "compare"


command = Commands()


class Command:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def run(self, args):
        pass


class HelpCmd(Commands):
    def run(self, args):
        print(f"\nUsage: "
              f"\njson-compare-tools --option <arguments>"
              f"\njson-compare-tools --{command.HELP} show usage"
              f"\njson-compare-tools --{command.CREATE_MAPPING_TEMPLATE} exp_json_file dps_json_file mapping_template_file"
              f"\njson-compare-tools --{command.CREATE_SORTING_RULES} mapping_template_file"
              f"\njson-compare-tools --{command.COMPARE} exp_json_file dps_json_file mapping_template_file sorting_rules_file")

class MappingTemplateCmd(Commands):

    def run(self, args):
        if len(args) >= 2:
            exp_json_file = args[0]
            dps_json_file = args[1]
            mapping_template_file = args[2]
        else:
            print(f"{command.CREATE_MAPPING_TEMPLATE} require at least 2 arguments but only have {len(args)}")
    def load_file(file):
    def process(self, exp_json_file, dps_json_file, mapping_template_file):
