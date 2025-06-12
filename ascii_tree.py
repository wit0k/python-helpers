import collections.abc
from itertools import count
import re
import json
import pandas as pd
from io import StringIO

def dict_to_ascii_tree(data: dict, prefix: str = "", level: int = 0) -> str:
    """
    Generates a visually precise ASCII art representation of a nested dictionary.

    This version implements a clear rule: keys for nodes whose values are
    lists are not displayed, providing a clean focus on the list content.

    Args:
        data: The dictionary to represent.
        prefix: The string prefix for drawing lines (internal use).
        level: The current nesting depth (internal use).

    Returns:
        A string containing the ASCII art representation of the dictionary.
    """
    if not isinstance(data, collections.abc.Mapping):
        return str(data)

    output_lines = []
    items = list(data.items())

    for i, (key, value) in enumerate(items):
        is_last = (i == len(items) - 1)
        is_branch = isinstance(value, collections.abc.Mapping) and value

        # --- 1. Determine connectors for the tree structure ---
        if level == 0:
            connector = ""
            child_prefix_ext = "    " if is_last else "│   "
            box_corner_char = "┌" if i == 0 else "└"
        else:
            connector = "└── " if is_last else "├── "
            child_prefix_ext = "    " if is_last else "│   "
            box_corner_char = connector[0]

        # --- 2. Prepare the content to be displayed inside the box ---
        content_lines = []
        if is_branch:
            # For dictionaries, always show the key.
            content_lines.append(f" {key} ")
        elif isinstance(value, list):
            # NEW, SIMPLIFIED LOGIC: If the value is a list, never show the key.
            if value:
                content_lines.extend([f"  - {item}    " for item in value])
            else:
                content_lines.append("  (empty list)")
        else:
            # For all other leaf types (strings, numbers, etc.), show the key.
            node_text = f"{value}" if key == "" else f"{key}: {value}"
            content_lines.append(f" {node_text} ")

        # --- 3. Calculate the required width of the box ---
        box_width = max(len(line) for line in content_lines) if content_lines else 0

        # --- 4. Draw the complete box for the current node ---
        box_top_line = f"{box_corner_char}─{'─' * box_width}─┐"
        box_bottom_line = f"{box_corner_char}─{'─' * box_width}─┘"

        if level == 0:
            output_lines.append(box_top_line)
            for line in content_lines:
                output_lines.append(f"│ {line.ljust(box_width)} │")
            output_lines.append(f"└─{'─' * box_width}─┘")
        else:
            output_lines.append(f"{prefix}{box_top_line}")
            for line in content_lines:
                output_lines.append(f"{prefix}│ {line.ljust(box_width)} │")
            output_lines.append(f"{prefix}{box_bottom_line}")

        # --- 5. If it's a branch, recurse into its children ---
        if is_branch:
            recursion_prefix = prefix + child_prefix_ext
            child_tree = dict_to_ascii_tree(value, prefix=recursion_prefix, level=level + 1)
            if child_tree:
                output_lines.append(child_tree)

    return "\n".join(filter(None, output_lines))

def str_path_to_nested_dict(tree_path: str, last_key_value=None, key_fn_pattern:str=r'(::\[(.*)\])$') -> dict:
    """
    Creates a nested dictionary from a slash-separated path string.

    Args:
        tree_path: The input path string (e.g., '/a/b/c').
        value: The value to set at the end of the path. Defaults to an empty dict.

    Returns:
        A nested dictionary representing the path.
    """
    if last_key_value is None: value = {}
    if tree_path is None: raise Exception('Cannot be None!')

    if not tree_path or tree_path == '/':
        return {}

    # Split the path into keys, filtering out empty strings from leading/trailing slashes
    keys = [key for key in tree_path.split('/') if key]

    result = {}
    current_level = result

    # Iterate through keys to build the nested structure
    for i, key in enumerate(keys):

        if key_fn_pattern is not None:
            fn_name_match = re.search(key_fn_pattern, key, re.IGNORECASE)
            if fn_name_match:
                fn_name = fn_name_match.group(2)
                fn_name_invocation = fn_name_match.group(1)
                key = key.replace(fn_name_invocation, '')
            else:
                fn_name = None

        if i == len(keys) - 1:
            # Last key, assign the final value
            current_level[key] = last_key_value
        else:
            # Create a new dictionary for the next level
            current_level[key] = {}
            # Move down to the next level
            current_level = current_level[key]

    return result

def dataframe_to_nested_dict(df, template: dict) -> dict:
    """
    Dynamically creates a nested dictionary from a DataFrame based on a template.

    The template defines the hierarchy for grouping. The keys of the template
    should correspond to column names in the DataFrame. The recursion stops when
    it encounters a final value string (which implies listing the values of that column)
    or a dictionary containing an 'agg' key.

    The 'agg' dictionary specifies the aggregation to perform:
    - 'agg': The aggregation function name (e.g., 'list', 'unique', 'count', 'sum', 'first').
    - 'values': The column to perform the aggregation on (not required for 'count').

    Args:
        df (pd.DataFrame): The input pandas DataFrame.
        template (dict): A nested dictionary that defines the output structure.

    Returns:
        dict: The formatted nested dictionary.
    """

    def recursive_builder(current_df: pd.DataFrame, current_template: dict or str) -> dict:
        # Base Case 1: The template is a string, implying a simple list aggregation.
        if isinstance(current_template, str):
            return current_df[current_template].tolist()

        # Base Case 2: The template is a dictionary specifying an aggregation.
        if 'agg' in current_template:
            agg_func = current_template['agg']
            column = current_template.get('values')

            if agg_func == 'count':
                return len(current_df)

            if not column:
                raise ValueError(f"A 'values' key is required for '{agg_func}' aggregation.")

            if agg_func == 'list':
                return current_df[column].tolist()
            elif agg_func == 'unique':
                return current_df[column].unique().tolist()
            elif agg_func == 'first':
                return current_df[column].iloc[0] if not current_df.empty else None
            elif agg_func == 'sum':
                return current_df[column].sum()
            else:
                raise ValueError(f"Unsupported aggregation function: '{agg_func}'")

        # Recursive Step: The template is a dictionary for grouping.
        group_by_column = list(current_template.keys())[0]
        next_template = current_template[group_by_column]

        output_dict = {}
        grouped = current_df.groupby(group_by_column)

        for group_name, group_df in grouped:
            output_dict[group_name] = recursive_builder(group_df, next_template)

        return output_dict

    return recursive_builder(df, template)


""""
#Examples:

##str_path_to_nested_dict:

print(json.dumps(str_path_to_nested_dict(tree_path='/a/b/c::[get_day]/d', last_key_value={}), indent=4, sort_keys=True))
print(json.dumps(str_path_to_nested_dict(tree_path='/a/b/c/d', last_key_value={}), indent=4, sort_keys=True))

# Gives:
{
    "a": {
        "b": {
            "c": {
                "d": {}
            }
        }
    }
}

## dict_to_ascii_tree:

example_dict = {
    'A': {
        'B': {
            'C': {
                '1': [
                    'ABC',
                    'ABCDEF'
                ],
                '2': [
                    'XXXXXXXXX'
                    'YYYYYYYYY'
                ],
            }
        }
    }
}

print(dict_to_ascii_tree(example_dict))

# Gives:
┌─────┐
│  A  │
└─────┘
    └─────┐
    │  B  │
    └─────┘
        └─────┐
        │  C  │
        └─────┘
            ├────────────────┐
            │   - ABC        │
            │   - ABCDEF     │
            ├────────────────┘
            └────────────────────────────┐
            │   - XXXXXXXXXYYYYYYYYY     │
            └────────────────────────────┘
            
## dataframe_to_nested_dict:

csv_data = \"""collection_date,bucket_id,fruit_color,fruit_type,quantity
2025-06-07,B1,Red,Apple,10
2025-06-07,B1,Green,Apple,5
2025-06-07,B1,Yellow,Banana,12
2025-06-07,B2,Red,Strawberry,30
2025-06-07,B2,Red,Apple,8
2025-06-08,B1,Green,Grape,25
2025-06-08,B2,Purple,Grape,20
2025-06-08,B1,Yellow,Banana,15
\"""

df = pd.read_csv(StringIO(csv_data))

template = {
    'fruit_color': {
        'fruit_type': {
            'bucket_id': {
                'agg': 'count'
            }
        }
    }
}

print(json.dumps(dataframe_to_nested_dict(df, template), indent=4, sort_keys=True))

# Gives:

{
    "Green": {
        "Apple": {
            "B1": 1
        },
        "Grape": {
            "B1": 1
        }
    },
    "Purple": {
        "Grape": {
            "B2": 1
        }
    },
    "Red": {
        "Apple": {
            "B1": 1,
            "B2": 1
        },
        "Strawberry": {
            "B2": 1
        }
    },
    "Yellow": {
        "Banana": {
            "B1": 2
        }
    }
}
"""