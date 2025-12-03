# BMAD Method - Gemini CLI Instructions

## Activating Agents

BMAD agents are defined in their respective `.md` files (e.g., within `.bmad/bmm/agents/`, `.bmad/cis/agents/`, `.bmad/core/agents/`) and are configured for the Gemini CLI via `.toml` files in `.gemini/commands/`.

### How to Use

1. **Type Trigger**: Use `*{agent-name}` in your prompt
2. **Activate**: Agent persona activates based on its configuration
3. **Continue**: Agent remains active for conversation

### Examples

```
*dev - Activate development agent
*architect - Activate architect agent
*test - Activate test agent
```

### Notes

- Agents are loaded individually based on their configuration.
- Triggers with asterisk: `*{agent-name}`
- Context for an agent includes its specific configuration.
