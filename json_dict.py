import re

class JsonHelperFormatters:

    def Highest(res):
        if len(res) > 0:
            return max(res)
        else:
            return res

    def Unique(res):
        try:
            if isinstance(res, list):
                res = list(set(res))
            return res
        except Exception as e:
            return res

    def WithoutZerosAndNulls(res):
        try:
            if isinstance(res, list):
                res = [x for x in res if x > 0 and x is not None]
            return res
        except Exception as e:
            return res

    def AverageFromList(res):
        try:
            if isinstance(res, list):
                return sum(res) / len(res)
            return res
        except Exception as e:
            return res

    def SumFromList(res):
        try:
            if isinstance(res, list):
                return sum(res)
            return res
        except Exception as e:
            return res

class JsonHelper(object):
    macros = ['{*}', '[*]', '{R:(']

    def __init__(self, data: dict):
        self.data = data

    def without_keys(self, keys, d=None):
        if d == None: d = self.data
        return {x: d[x] for x in d if x not in keys}

    def with_keys(self, d, keys):
        if d == None: d = self.data
        return {x: d[x] for x in d.keys() if x in keys}

    def get(self, value_path: str, default, nested_dict=None, results=None, formatter=None, where=None):
        """
        Macros:
         - {*} - Go over all dict keys (at current depth)
         - [*] - Go over all list elements (at current depth)
         - {R:(<pattern>)} - Go over all dict keys (at current depth) that match given <pattern>
        """
        if formatter is None: formatter = []

        def format_result(res, where=None):
            for fmember in formatter:
                formatter_fn = getattr(JsonHelperFormatters, fmember, None)
                if formatter_fn:
                    if where is None:
                        return formatter_fn(res)
                else:
                    if where is None:
                        return res

            return res

        def is_macro(_str) -> bool:

            if _str in self.macros: return True

            for macro_str in self.macros:
                if _str.startswith(macro_str): return True

            return False

        if results is None: results = []

        if nested_dict is None:
            data = {}
        else:
            data = nested_dict

        value_path_sequence = value_path.split('/')
        sequence_len = len(value_path_sequence)

        for path_element in value_path_sequence:

            if path_element == '':
                data = self.data
                sequence_len -= 1

                if sequence_len <= 0:
                    return format_result(data, where)
                else:
                    continue

            if not is_macro(path_element):
                data = data.get(path_element, {})
                sequence_len -= 1

                if isinstance(data, dict):
                    if not len(data.keys()) > 0:
                        return default

                if sequence_len <= 0:
                    return format_result(data, where)
                else:
                    continue

            if '{*}' in path_element:
                sequence_len -= 1

                if sequence_len <= 0:
                    return format_result(data, where)

                for key in data.keys():
                    res = self.get(
                        value_path='%s/%s' % (key, '/'.join(value_path_sequence[-sequence_len:])),
                        default=default,
                        nested_dict={'%s' % key: data[key]},
                    )

                    if isinstance(res, list):
                        results.extend(res)
                    else:
                        results.append(res)

                return format_result(results, where)

            if '[*]' in path_element:
                sequence_len -= 1

                if sequence_len <= 0:
                    return format_result(data, where)

                for element in data:
                    res = self.get(
                        value_path='%s' % '/'.join(value_path_sequence[-sequence_len:]),
                        default=default,
                        nested_dict=element,
                    )

                    if isinstance(res, list):
                        results.extend(res)
                    else:
                        results.append(res)

                return format_result(results, where)

            # {R:(Key_Pattern)}
            if '{R:(' in path_element:
                sequence_len -= 1  # A fix is necessary when sequence will be 0
                key_patterns = re.search(r'\{R:\((.+)?\)\}', path_element, re.IGNORECASE)

                if key_patterns:
                    for key in data.keys():
                        for key_pattern in key_patterns.groups():
                            if re.match(key_pattern, key, re.IGNORECASE):
                                res = self.get(
                                    value_path='%s/%s' % (key, '/'.join(value_path_sequence[-sequence_len:])),
                                    default=default,
                                    nested_dict={'%s' % key: data[key]},
                                )

                                if isinstance(res, list):
                                    results.extend(res)
                                else:
                                    results.append(res)
                            else:
                                pass

                return format_result(results, where)