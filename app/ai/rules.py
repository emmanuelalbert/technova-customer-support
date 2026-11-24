from app.ai.schemas import Issue

# These are customer-facing steps that do not commit TechNova to fulfilment.
CUSTOMER_STEPS = {"troubleshoot", "ask-details"}


def resolve_issue(issue: Issue) -> str:
    """Return a proposed next step. Python decides; the model does not authorize fulfilment."""
    step = next_step(issue)
    if step not in CUSTOMER_STEPS and not issue.order_number:
        return "ask-details"
    return step


def next_step(issue: Issue) -> str:
    if issue.problem == "missing-accessory":
        return "colleague-review-missing-accessory"

    if issue.problem in {
        "charging",
        "bluetooth-pairing",
        "sound-quality",
        "microphone",
        "display",
        "notifications",
        "activity-tracking",
    }:
        if issue.troubleshooting_attempted:
            return "colleague-review-unresolved-product-issue"
        return "troubleshoot"

    if issue.problem in {
        "water-damage",
        "physical-damage",
        "possible-manufacturing-fault",
    }:
        return "colleague-review-product-condition-or-warranty"

    return "escalate"
