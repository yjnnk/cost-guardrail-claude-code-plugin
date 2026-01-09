# Cost Guardrails Plugin for Claude Code

Automatically track your Claude Code spending and get warnings when approaching your monthly budget limit.

## Features

- **Automatic cost tracking**: Parses Claude Code usage logs to calculate spending
- **Monthly budget limit**: Set to $15/month (configurable)
- **Smart warnings**: Alerts at 50%, 75%, 90%, 100%, and 125% of budget
- **No duplicate warnings**: Only shows warnings when threshold increases
- **Session summaries**: Brief cost summary when you end a session
- **Standalone command**: Check your status anytime

## Installation

The plugin should be installed at:
```
~/.claude/plugins/cost-guardrails/
```

It will automatically activate on your next Claude Code session.

## How It Works

### Automatic Monitoring

The plugin uses Claude Code's hook system to:

1. **At Session Start**: Check your spending and show warnings if you've crossed thresholds
2. **At Session End**: Display a brief summary of your monthly spending

### Warning Levels

- **50%**: Informational notice
- **75%**: You're using most of your budget
- **90%**: Approaching the limit
- **100%**: Budget exceeded
- **125%**: Significantly over budget

### Current Status

You're currently at **26.6% of your budget** ($3.98 / $15.00).

## Manual Status Check

Run the standalone command anytime to see detailed cost breakdown:

```bash
~/.claude/plugins/cost-guardrails/commands/cost-status.sh
```

Or create an alias in your shell:
```bash
alias claude-cost='~/.claude/plugins/cost-guardrails/commands/cost-status.sh'
```

Then run:
```bash
claude-cost
```

## Configuration

Edit the budget and settings in:
```
~/.claude/plugins/cost-guardrails/config/budget_config.json
```

Available options:
- `monthly_budget`: Your spending limit (default: $15.00)
- `warning_thresholds`: When to show warnings (default: [50, 75, 90, 100, 125])
- `enabled`: Turn plugin on/off (default: true)
- `show_session_start_warnings`: Show warnings at session start (default: true)
- `show_stop_summaries`: Show summaries at session end (default: true)

## State File

The plugin tracks warning state in:
```
~/.claude/cost_guardrails_state.json
```

This prevents duplicate warnings and tracks which warnings you've already seen.

## How Costs Are Calculated

The plugin uses official Anthropic pricing (as of January 2025):

**Claude Sonnet 4.5:**
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens
- Cache write: $3.75 per million tokens
- Cache read: $0.30 per million tokens

**Claude Haiku 4.5:**
- Input: $0.80 per million tokens
- Output: $4.00 per million tokens
- Cache write: $1.00 per million tokens
- Cache read: $0.08 per million tokens

## Tips to Reduce Costs

If you're approaching your budget:

1. **Use `/compact`**: Reduce context size to lower cache costs
2. **Switch to Haiku**: Use `/model haiku` for simpler tasks (80% cheaper)
3. **Break tasks down**: Smaller, focused tasks use less context
4. **Clear history**: Use `/clear` between unrelated tasks
5. **Be specific**: Precise queries avoid expensive exploratory searches

## Troubleshooting

### Plugin not showing warnings

The plugin only shows warnings when you cross new thresholds. If you're at 26%, you won't see warnings until you reach 50%.

### Check plugin status

Run the standalone command:
```bash
~/.claude/plugins/cost-guardrails/commands/cost-status.sh
```

### View state

Check what warnings have been shown:
```bash
cat ~/.claude/cost_guardrails_state.json
```

### Reset warnings

To see warnings again (useful for testing):
```bash
rm ~/.claude/cost_guardrails_state.json
```

## Technical Details

- **Data source**: `~/.claude/projects/**/*.jsonl` files
- **Language**: Python 3.7+
- **Hook events**: SessionStart, Stop
- **State tracking**: JSON file in `~/.claude/`

## Privacy

All data stays on your local machine. The plugin:
- ✅ Reads JSONL files locally
- ✅ Stores state locally
- ✅ No network requests
- ✅ No data sent anywhere

## Support

For issues or questions:
1. Check the README (this file)
2. Run the standalone command to verify it's working
3. Check `~/.claude/cost_guardrails_state.json` for state
4. Review logs in `~/.claude/debug/` if available

## Version

Current version: 1.0.0

## License

Personal use - created for monitoring Claude Code spending.
# cost-guardrail-claude-code-plugin
