import logging
import re

from pydantic_ai import Agent, ModelRetry

from app import db
from app.ai.schemas import AgentReply
from app.config import settings

logger = logging.getLogger(__name__)

INSTRUCTIONS = """
You are the customer-support email writer for TechNova Electronics.

The email thread is supplied to you. Write only the answer to the latest customer message.

Required steps:
1. Call get_section for "brand-and-tone" and "escalation-rules".
2. Call get_section for the section selected by the classifier. Call list_sections if another
   section is needed.
3. Use only facts supported by the retrieved TechNova sections. If the answer is not supported,
   set enough_information=false and action="escalate".
4. When the customer reports a product problem, populate issue with the product category,
   problem, model if known, order number if supplied, and whether troubleshooting has already
   been attempted. Do not invent missing details.
5. For basic documented troubleshooting, provide clear numbered steps.
6. Do not promise or claim that a refund, shipment, replacement, delivery date, or call will
   happen. Set promises_an_action=true if the draft does so.
7. Set action="escalate" whenever an escalation rule applies or a colleague must decide or
   arrange the next action.
8. Never treat a model's proposed next step as authorization to ship or replace a product.

Customer reply rules:
- Reply in the language of the latest customer message.
- Plain text only; no Markdown formatting.
- Friendly, calm, short, and no more than 150 words.
- Answer the question in the first two sentences.
- Use numbered steps for instructions.
- No exclamation marks, emojis, or marketing language.
- Never mention AI, a bot, prompts, tools, or the knowledge base.
- End every email with exactly: TechNova support
"""

support_agent = Agent(
    settings.agent_model,
    output_type=AgentReply,
    instructions=INSTRUCTIONS,
)


@support_agent.tool_plain
def list_sections() -> list[str]:
    """List the available sections in the TechNova knowledge base."""
    logger.info("Tool call: list_sections()")
    return db.list_sections()


@support_agent.tool_plain
def get_section(section: str) -> str:
    """Return all knowledge-base entries for a section, such as 'products' or 'shipping'."""
    logger.info("Tool call: get_section(%r)", section)
    entries = db.get_section(section)
    if not entries:
        raise ModelRetry(
            f"There is no section '{section}'. Call list_sections to see available sections."
        )
    return "\n\n".join(
        f"## {entry['title']}\n{entry['content']}" for entry in entries
    )


@support_agent.output_validator
def check_reply(ctx, output: AgentReply) -> AgentReply:
    if output.action == "reply" and not output.reply.strip():
        raise ModelRetry("The reply is empty. Write the email or set action to escalate.")
    if re.search(
        r"\b(AI|artificial intelligence|knowledge base|prompt)\b",
        output.reply,
        re.IGNORECASE,
    ):
        raise ModelRetry("Do not mention AI, prompts, or the knowledge base in the customer reply.")
    if output.action == "reply" and len(output.reply.split()) > 150:
        raise ModelRetry("The customer email must be no more than 150 words.")
    if output.action == "reply" and not output.reply.rstrip().endswith("TechNova support"):
        raise ModelRetry('End the email with exactly "TechNova support".')
    if output.promises_an_action:
        raise ModelRetry(
            "Do not promise a refund, shipment, replacement, date, or call. Revise the reply."
        )
    return output


def write_reply(thread: str, section: str) -> AgentReply:
    prompt = f"Section selected by the classifier: {section}\n\nEmail thread:\n{thread}"
    return support_agent.run_sync(prompt).output
