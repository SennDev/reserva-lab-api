import re


def generate_prefixed_code(model_class, prefix: str, width: int = 3, field_name: str = "id") -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    last_number = 0

    for value in model_class.objects.values_list(field_name, flat=True):
        match = pattern.match(str(value))
        if match:
            last_number = max(last_number, int(match.group(1)))

    return f"{prefix}-{last_number + 1:0{width}d}"
