

INTERVAL_IN_MINUTES = {
    'm': 1,
    'h': 60,
    'd': 1440,
    'w': 10080,
    'mon': 43200,
    'y': 525600
}


def minute_to_interval(minutes: float) -> str:    
    values = sorted(INTERVAL_IN_MINUTES.items(), key=lambda x: x[1], reverse=True)

    for key, value in values:
        by_units = minutes / value

        if by_units >= 1:
            unit_format = f"{by_units:.1f}"
            return f"{unit_format[:-2]}{key}" if unit_format.endswith('.0') else f"{by_units:.1f}{key}"
        
    return '<1m'
