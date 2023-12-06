schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "url": {"type": "string", "format": "uri"},
            "width": {"type": "integer"},
            "height": {"type": "integer"}
        },
        "required": ["id", "url", "width", "height"],
        "additionalProperties": False
    }
}
