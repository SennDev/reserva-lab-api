from datetime import time


def parse_time_slot(slot: str) -> tuple[time, time]:
    try:
        start_text, end_text = [part.strip() for part in slot.split("-", maxsplit=1)]
        start_hour, start_minute = [int(part) for part in start_text.split(":", maxsplit=1)]
        end_hour, end_minute = [int(part) for part in end_text.split(":", maxsplit=1)]
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("La franja horaria no tiene un formato valido.") from exc

    start = time(hour=start_hour, minute=start_minute)
    end = time(hour=end_hour, minute=end_minute)

    if start >= end:
        raise ValueError("La hora de inicio debe ser menor que la hora de fin.")

    return start, end


def time_slots_overlap(first_slot: str, second_slot: str) -> bool:
    first_start, first_end = parse_time_slot(first_slot)
    second_start, second_end = parse_time_slot(second_slot)

    return first_start < second_end and second_start < first_end
