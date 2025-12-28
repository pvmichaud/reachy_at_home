# ADR-004: LLM Strategy

## Status
**Approved** — 2024-12-21

## Context

The Reachy Home Assistant needs natural language understanding and generation for:

1. **Conversation**: Natural dialogue with family members
2. **Intent parsing**: Understanding what users want
3. **Response generation**: Helpful, contextual replies
4. **Summarization**: Briefings, schedule summaries
5. **Reasoning**: Multi-step planning and problem solving

### Key Requirements
- Natural, family-friendly conversation
- Reliable intent understanding
- Contextual awareness (who's talking, time of day, recent events)
- Reasonable latency (<2 seconds for typical responses)
- Cost-effective for daily household use

## Decision

**Claude API (Anthropic) as the primary LLM, with structured prompting and tool use.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LLM Integration                          │
│                                                                  │
│  ┌─────────────┐     ┌──────────────────┐     ┌──────────────┐  │
│  │   User      │────▶│  Prompt Builder  │────▶│  Claude API  │  │
│  │   Input     │     │                  │     │              │  │
│  └─────────────┘     │  - System prompt │     │  - Sonnet    │  │
│                      │  - User context  │     │  - Tool use  │  │
│  ┌─────────────┐     │  - Memory        │     │              │  │
│  │   Memory    │────▶│  - Calendar      │     └──────────────┘  │
│  │   Store     │     │  - Conversation  │            │          │
│  └─────────────┘     └──────────────────┘            ▼          │
│                                               ┌──────────────┐  │
│                                               │   Response   │  │
│                                               │   Handler    │  │
│                                               └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Model Selection

| Use Case | Model | Rationale |
|----------|-------|-----------|
| Conversation | Claude Sonnet | Good balance of quality/speed/cost |
| Complex reasoning | Claude Sonnet | Sufficient for household tasks |
| Quick responses | Claude Haiku | For simple acknowledgments |

### System Prompt Structure

```markdown
You are Reachy, a friendly household assistant robot helping the Michaud family.

## Family Members
- Patrick (dad): Software engineer, works from home
- Leah (mom): [occupation], manages family calendar
- Cam (son, 8): 3rd grade, loves dinosaurs
- Reese (daughter, 6): 1st grade, artistic

## Current Context
- Time: {current_time}
- Speaking with: {current_user}
- Location: Kitchen
- Today's events: {calendar_summary}

## Relevant Memories
{retrieved_memories}

## Guidelines
- Be warm, helpful, and age-appropriate
- Keep responses concise (we're a robot, not a lecture)
- For kids: simple language, encouraging tone
- For parents: efficient, actionable information
- Reference past interactions naturally
- If unsure, ask clarifying questions
```

### Tool Use

Claude supports tool use for structured actions:

```python
tools = [
    {
        "name": "set_reminder",
        "description": "Set a reminder for a family member",
        "parameters": {
            "user": "string",
            "message": "string",
            "time": "datetime"
        }
    },
    {
        "name": "check_calendar",
        "description": "Look up calendar events",
        "parameters": {
            "user": "string",
            "date_range": "string"
        }
    },
    {
        "name": "add_to_list",
        "description": "Add item to shopping or todo list",
        "parameters": {
            "list_type": "shopping|todo",
            "item": "string"
        }
    }
]
```

## Consequences

### Positive
- **Natural conversation**: Claude excels at natural dialogue
- **Context handling**: Large context window for memories
- **Tool use**: Structured actions via function calling
- **Safety**: Built-in safety for family environment
- **Reliability**: Production-ready API

### Negative
- **Internet required**: API calls need connectivity
- **Cost**: ~$0.003-0.015 per conversation turn
- **Latency**: 500ms-2s for responses
- **Privacy consideration**: Conversations sent to API

### Cost Estimation

| Usage Pattern | Daily Calls | Monthly Cost |
|--------------|-------------|--------------|
| Light (10 interactions/day) | ~30 | ~$3-5 |
| Medium (30 interactions/day) | ~90 | ~$10-15 |
| Heavy (60 interactions/day) | ~180 | ~$20-30 |

### Privacy Approach

1. **Minimize PII**: Don't send unnecessary personal details
2. **Anonymize when possible**: "the 8-year-old" vs full names
3. **Local memory**: Keep detailed memories local, send summaries
4. **User awareness**: Family knows conversations are processed

## Implementation Notes

### Client Setup
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
```

### Conversation Handler
```python
async def chat(
    user_input: str,
    user: User,
    conversation_history: list
) -> str:
    """Process a conversation turn."""

    # Retrieve relevant memories
    memories = await retrieve_context(user_input, user.id)

    # Build messages
    messages = [
        {"role": "user", "content": m.content} if m.role == "user"
        else {"role": "assistant", "content": m.content}
        for m in conversation_history[-10:]  # Last 10 turns
    ]
    messages.append({"role": "user", "content": user_input})

    # Call Claude
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=build_system_prompt(user, memories),
        messages=messages,
        tools=tools
    )

    return response.content
```

### Caching Strategy
```python
# Cache common queries
@cache(ttl=300)  # 5 minutes
async def get_calendar_summary(date: date) -> str:
    """Get cached calendar summary."""
    events = await get_events_for_date(date)
    return format_calendar_summary(events)
```

## Future Considerations

1. **Local LLM fallback**: Run smaller model for offline/simple queries
2. **Response caching**: Cache common greetings/responses
3. **Streaming**: Stream responses for better UX
4. **Fine-tuning**: If needed for family-specific patterns

## Related Decisions
- ADR-003: Memory architecture (provides context)
- ADR-005: Speech pipeline (STT/TTS around LLM)
