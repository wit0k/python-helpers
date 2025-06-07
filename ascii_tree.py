import collections.abc

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

def dict_to_ascii_tree_old(data, prefix="", is_last_sibling_group=True, level=0):
    """
    Generates a visually precise ASCII art representation of a nested dictionary.

    Args:
        data: The dictionary to represent.
        prefix: The string prefix for drawing lines (internal use).
        is_last_sibling_group: Boolean indicating if the current node is the last
                               in its parent's item list (internal use).
        level: The current nesting depth (internal use).

    Returns:
        A string containing the ASCII art representation of the dictionary.
    """
    output = []
    items = list(data.items())
    # pointers determine the connector type (e.g., ├── or └──) for each item
    pointers = ["├── "] * (len(items) - 1) + ["└── "] if items else []

    for i, (key, value) in enumerate(items):
        connector_str = pointers[i]  # The full connector string like "├── " or "└── "
        connector_char = connector_str[0]  # The first char like '├' or '└'

        if key == '':
            pass

        is_current_node_last = (i == len(items) - 1)

        if isinstance(value, dict) and value:  # Node is a parent (a non-empty dictionary)
            node_text = f" {key} "
            max_child_key_len = 0
            if value:  # Check again, as value might be an empty dict
                max_child_key_len = max(len(str(k)) for k in value.keys())

            current_node_width = len(node_text)
            # Box width ensures space for text and some alignment for children visual cues
            box_content_width = max(current_node_width,
                                    max_child_key_len + 2 if max_child_key_len > 0 else current_node_width)
            # Total box width for string formatting (excluding prefix and connector char for non-roots)
            # For ljust, it's content area. Top/bottom lines use box_content_width directly for dashes.
            # The -1 for ljust comes from space + text + space = content_width, text fills (content_width - 2)
            # So ljust should be on node_text not box_width
            # Effective content area for text: box_content_width - 2 (for spaces)
            # Let's define box_drawing_width = box_content_width + 2 for padding " text "

            # Simplified box_width for drawing dashes and ljust padding
            # The number of dashes needed. +2 for the spaces around node_text
            actual_box_inner_width = len(node_text)
            # Parent box width needs to be at least its text, or accommodate children signals
            min_width_for_children_signal = 0
            if value:  # If it has children
                # This heuristic tries to make parent box look reasonable for children
                # A bit of trial and error might be needed for perfect aesthetics in all cases
                min_width_for_children_signal = max(len(str(k)) for k in value.keys()) + 2 if value else 0

            # Overall width for the content part of the box (between '│' and '│' or '┌'/'└' and '┐'/'┘')
            # This includes the spaces padding the text
            render_box_content_width = max(len(node_text), min_width_for_children_signal)

            if level == 0 and i == 0:  # Root node treatment
                output.append(prefix + "┌─" + "─" * render_box_content_width + "─┐")
                output.append(prefix + "│ " + node_text.ljust(render_box_content_width) + " │")
                output.append(prefix + "└─" + "─" * render_box_content_width + "─┘")
            else:  # Non-root parent nodes
                output.append(prefix + connector_char + "─" + "─" * render_box_content_width + "─┐")
                output.append(prefix + connector_char + " " + node_text.ljust(render_box_content_width) + " │")
                output.append(prefix + connector_char + "─" + "─" * render_box_content_width + "─┘")

            # Extension for children's prefix
            # If current node is "├──", its children's prefix needs "│   "
            # If current node is "└──", its children's prefix needs "    "
            extension = "│   " if connector_char == "├" else "    "
            output.append(dict_to_ascii_tree_old(value, prefix + extension, is_current_node_last, level + 1))

        else:  # Node is a leaf (value is not a dict or is an empty dict)
            leaf_text = f" {key}: {value} "
            render_leaf_box_content_width = len(leaf_text)

            if key == '' and isinstance(value, list):
                render_leaf_box_content_width = max([len(f" {key}  {s}    ") for s in value])
                output.append(prefix + connector_char + "─" + "─" * render_leaf_box_content_width + "─┐")
                for s in value:
                    leaf_text = f" {key}  {s} "
                    output.append(prefix + connector_char + " " + leaf_text.ljust(render_leaf_box_content_width) + " │")
                output.append(prefix + connector_char + "─" + "─" * render_leaf_box_content_width + "─┘")
            else:
                if level == 0 and i == 0:  # Root leaf node treatment
                    output.append(prefix + "┌─" + "─" * render_leaf_box_content_width + "─┐")
                    output.append(prefix + "│ " + leaf_text.ljust(render_leaf_box_content_width) + " │")
                    output.append(prefix + "└─" + "─" * render_leaf_box_content_width + "─┘")
                else:  # Non-root leaf nodes
                    output.append(prefix + connector_char + "─" + "─" * render_leaf_box_content_width + "─┐")
                    output.append(prefix + connector_char + " " + leaf_text.ljust(render_leaf_box_content_width) + " │")
                    output.append(prefix + connector_char + "─" + "─" * render_leaf_box_content_width + "─┘")

    return "\n".join(line for line in output if line.strip() or "\n" in line)

""""
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
# print(dict_to_ascii_tree_old(example_dict))

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

"""