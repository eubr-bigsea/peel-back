from zoneinfo import ZoneInfo

def changeTimezone(model, timezone="America/Sao_Paulo"):
    utc = ZoneInfo("UTC")
    localtz = ZoneInfo(timezone)
    model.created = model.created.replace(tzinfo=utc).astimezone(localtz)
    model.updated = model.updated.replace(tzinfo=utc).astimezone(localtz)

