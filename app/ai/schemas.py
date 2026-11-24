from typing import Literal

from pydantic import BaseModel, Field

Section = Literal[
    "products",
    "setup-support",
    "returns-and-warranty",
    "shipping-policy",
    "voice-and-tone",
    "escalation-rules",
    "other",
]

Product = Literal["headphones", "smartwatch", "speaker"]
Problem = Literal[
    "missing-accessory",
    "charging",
    "bluetooth-pairing",
    "sound-quality",
    "microphone",
    "display",
    "notifications",
    "activity-tracking",
    "water-damage",
    "physical-damage",
    "possible-manufacturing-fault",
    "other",
]


class Classification(BaseModel):
    section: Section
    language: str = Field(description="Language of the latest customer message")
    needs_human: bool = Field(description="True when an escalation rule applies")
    reason: str = Field(description="Brief reason for the classification")
    acknowledgement: str = Field(
        description=(
            "Short acknowledgement in the customer's language. Confirm receipt "
            "and say a colleague will reply within one business day. Do not promise an outcome."
        )
    )


class Issue(BaseModel):
    product: Product
    problem: Problem
    model: str | None = None
    order_number: str | None = None
    delivery_date_or_age: str | None = None
    troubleshooting_attempted: bool = Field(
        default=False,
        description="True only when the customer says the documented troubleshooting was tried",
    )
    accessory_or_part: str | None = None
    details: str | None = None


class AgentReply(BaseModel):
    action: Literal["reply", "escalate"]
    reply: str = Field(description="Customer-facing email, plain text")
    reasoning: str = Field(description="Brief internal explanation of the knowledge used")
    enough_information: bool = Field(
        description="True only when the TechNova knowledge base supports the answer"
    )
    promises_an_action: bool = Field(
        description="True if the reply promises a refund, shipment, replacement, date, or call"
    )
    issue: Issue | None = Field(
        default=None, description="Populate when the customer reports a product problem"
    )


class Decision(BaseModel):
    action: Literal["reply", "escalate"]
    section: str
    reply: str
    reason: str
    proposed_action: str | None = None
