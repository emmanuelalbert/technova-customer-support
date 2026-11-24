import sys
from pathlib import Path

import nest_asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))

nest_asyncio.apply()

from app.ai.decide import decide

question = (
    "This is ridiculous. My headphones stopped working after two days. Order number: TN-918273. "
    "If you don't fix this immediately, I'm leaving a terrible review. "
    "I want someone to deal with this."
)

decision = decide(question)
print(decision.model_dump_json(indent=2))
