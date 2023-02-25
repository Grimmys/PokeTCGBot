def timestamp_to_relative_time_format(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"


def format_boolean_option_value(option_value: bool):
    return "✅" if option_value else "❌"
