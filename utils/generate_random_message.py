def generate_unique_message(prefix: str = "autotest") -> str:
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8]}"