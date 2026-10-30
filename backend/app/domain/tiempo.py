from datetime import datetime, timezone


def ahora_utc() -> datetime:
    """UTC sin zona (naive), que es como se guardan las fechas en la base."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
