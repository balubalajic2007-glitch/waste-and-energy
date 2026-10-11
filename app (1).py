"""Kabadi Mitra: Lambda handler. POST /estimate {"kg": {"news": 5, "pet": 2}, "ewaste": ["bat"]}"""
import json, os, time

RULES = json.load(open(os.path.join(os.path.dirname(__file__), "rules.json")))
TABLE = os.environ.get("TABLE_NAME")
ITEMS = {i["id"]: i for i in RULES["items"]}
EW = {e["id"]: e for e in RULES["ewaste"]}


def estimate(kg, ewaste=()):
    lines, total, co2 = [], 0.0, 0.0
    for k, v in kg.items():
        if k not in ITEMS:
            continue
        w = max(0.0, min(float(v), 500.0))
        if w == 0:
            continue
        it = ITEMS[k]
        amt = round(w * it["rate"], 2)
        lines.append({"item": it["name"], "kg": w, "rate": it["rate"], "amount": amt})
        total += amt
        co2 += w * it["co2"]
    flagged = [EW[e]["name"] for e in ewaste if e in EW]
    return {"lines": lines, "total_inr": round(total, 2), "co2_saved_kg": round(co2, 1),
            "ewaste": flagged, "ewaste_advice": RULES["ewaste_advice"] if flagged else None}


def handler(event, _ctx=None):
    try:
        body = json.loads(event.get("body") or "{}")
        kg = body["kg"]
        if not isinstance(kg, dict):
            raise TypeError
        result = estimate(kg, body.get("ewaste", []))
    except (KeyError, TypeError, ValueError):
        return {"statusCode": 400, "body": json.dumps({"error": "send {kg: {item: weight}}"})}
    if TABLE:  # running tally of kg diverted from landfill per neighbourhood
        import boto3
        boto3.resource("dynamodb").Table(TABLE).put_item(Item={
            "area": body.get("area", "demo"), "ts": int(time.time()),
            "total_inr": str(result["total_inr"]), "co2": str(result["co2_saved_kg"])})
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)}
