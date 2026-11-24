from app.ai.agent import write_reply
from app.ai.classifier import classify
from app.ai.rules import CUSTOMER_STEPS, resolve_issue
from app.ai.schemas import Decision


def decide(thread: str, has_attachments: bool = False) -> Decision:
    """Run classification, knowledge-grounded drafting, and Python policy checks."""
    classification = classify(thread)

    def escalate(reason: str, proposed_action: str | None = None) -> Decision:
        return Decision(
            action="escalate",
            section=classification.section,
            reply=classification.acknowledgement,
            reason=reason,
            proposed_action=proposed_action,
        )

    if has_attachments:
        return escalate("The email contains attachments")

    if classification.needs_human:
        return escalate(classification.reason)

    answer = write_reply(thread, classification.section)

    if answer.action == "escalate":
        return escalate(answer.reasoning)

    if not answer.enough_information:
        return escalate("The TechNova support information does not answer this question")

    proposed_action = None
    if answer.issue:
        proposed_action = resolve_issue(answer.issue)
        if proposed_action not in CUSTOMER_STEPS:
            return escalate(
                f"Human colleague review required: {proposed_action}",
                proposed_action=proposed_action,
            )

    if answer.promises_an_action:
        return escalate("The proposed reply promises an action")

    return Decision(
        action="reply",
        section=classification.section,
        reply=answer.reply,
        reason=answer.reasoning,
        proposed_action=proposed_action,
    )
