---
name: law-email-style
description: Draft emails, memos, and messages in your voice. Use when asked to draft, write, or compose any email or professional communication.
license: CC-BY-4.0
metadata:
  author: "[Your Name]"
---

# Law Email Style Guide

Use this guide for email-specific formatting. Voice, tone, banned phrases, and preferred expressions are defined in the **Writing & Tone** section of the global instructions (CLAUDE.md in Claude Code, AGENTS.md in Codex) — that baseline always applies. This skill adds email-specific structure on top.

**Load the `polk-voice-corpus` skill for anything going out under [Your Name]'s name.** It holds verified samples of his actual sent email, and where a sample and a rule disagree the sample wins — the rules were written from memory and have measurably drifted. It also carries the drift signature: the four edits (adding "Please", cutting exclamation points, dropping the joke, rounding off a specific count) that push a draft away from his voice without tripping any banned-phrase check.

## Voice Priorities (apply to every email)

These five rules are the most frequently violated in drafts. Apply them before anything else:

1. **Use contractions when they sound natural.** [Your Name] often writes "I'm", "we're", "can't", "won't", "it's", "that's", "let's", "don't", "I'd", and "you'll", especially in internal and semi-formal messages. Do not force a contraction into every email; the audience and sentence should decide.
2. **Never open with a preamble.** Do not start the first sentence (after the greeting) with "Thanks for reaching out", "I wanted to reach out", "I hope this email finds you well", "Thanks for your email", "Great question", "Absolutely", or "I'd be happy to help". Open with the substance directly.
3. **Use em-dashes naturally, but not mechanically.** [Your Name] uses em-dashes for asides, interruptions, and emphasis. Do not impose a numerical limit; revise only when repeated dashes make the sentence harder to follow. Never use em-dashes as bullet leaders.
4. **Never assert a conviction or a specific he has not given you.** Do not write superlatives in his voice ("the best thing I've read," "lands squarely"), do not strip his hedges ("pretty," "probably," "in some courses"), and do not invent sourced-looking detail — "I nagged you about this last August" became "I've reminded you about this many times" when the single instance was fabricated and the general pattern was the truth. Claim strength is his to set. When the substance warrants emphasis, state the fact and let him add the verdict. Measured on the 2026-08-30 office-hours reminder, where five of his edits were this one move; see the pair in `polk-voice-corpus/references/email-broadcast.md`.
5. **Never write a changelog into an email.** When the message follows work you just did, report the outcome, not the itemisation of it. On 2026-08-30 a reply to the colleague who prompted a site cleanup carried seventy words of what changed — sections merged, a tab down from about 2,000 words to under 800, eight items in a new list — and [Your Name] sent eleven: "You inspired Cluade and I to do a cleanup and reorg." Every cut sentence was accurate and properly hedged, so this is not rule 4; it is relevance. The recipient could see the changes on the site already, and he does not report metrics to colleagues. If you have just done a lot of work, assume the urge to describe it is yours and not his. See `polk-voice-corpus/references/email-replies.md`.

## Agent Dependencies

This skill dispatches sub-agents for pre-send quality checks. Each call is guarded — the email still produces without them, but factual and style verification are weaker.

- `factual-reviewer` — extracts discrete factual claims for verification.
- `fact-verifier` — live web/source verification of specific claims.
- `voice-style-checker` — voice, style, and AI-tell scan.

Each requires the agent on the current runtime: `~/.claude/agents/<name>/<name>.md` (Claude Code) or `~/.codex/agents/<name>.toml` (Codex).

## Greeting

Match the audience and formality:
- **Faculty-wide:** "Dear Colleagues," or "Dear Colleagues and Friends -"
- **Individual, semi-formal:** "Dear [First Name]," or "Hi [First Name] -"
- **Casual / internal:** "Good morning -" or just dive in with no greeting
- **Note:** The default style uses a hyphen after greetings rather than a comma

## Sign-Off

Every email must end with a sign-off line that is exactly `[Your Name]` (or `Best,` followed by a blank line and then `[Your Name]`). No title, no phone, no em-dash. Never end with "Sincerely,", "Regards,", "Warm regards,", "Cheers," or "All the best,". May include a warm closing line before the sign-off when the tone fits ("I look forward to seeing you next week." or "Let me know how I can help!").

## Email Structure

- Use **bold section headers** in longer emails to organize topics. No numbered sections for headers.
- **In email, use real indented lists** — plain markdown `-` items, which render as an indented `<ul>` with round markers, never a literal `•`. In **.docx** output the equivalent is a real Word list (see `law-memo` and `law-document`). Never em-dashes as bullet leaders, in any format.
- Numbered lists for sequential action items, deadlines, or options. Items that are merely parallel — one ask each for two different people, say — are a bulleted list, not a numbered one.
- "So," as a casual transition between sections.
- Run the AI Writing Tell Check in `law-document/references/voice-checks.md` (the `law-document` skill installed beside this one) before sending. Applies to emails too.
- **Automated review:** After drafting:
  1. If the `factual-reviewer` agent is available, spawn it to check all factual claims. Fix any issues it flags.
  2. If the factual reviewer lists claims needing live verification, if the `fact-verifier` agent is available, spawn it with those claims. Correct any contradicted claims; flag unverifiable ones for the user.
  3. If the `voice-style-checker` agent is available, spawn it to scan for style issues. Fix any issues it flags.
  Complete all steps before presenting to the user.

## Example Patterns

**Concise data request (casual, no greeting):**
> I'm working on gathering as much data as possible about our curriculum. Two pieces that would be very useful:
>
> The course finder data - ideally all the fields, as far back historically as possible, within reason.
> Evaluations data - again, ideally all the fields and as far back as possible.
>
> The data format etc doesn't really matter. Could just be flat csv export files or you could just point me to a database endpoint.
>
> I'm hoping this is pretty easy to put hands on - again, just an export of the database (or even a database dump) is fine. If it is tricky or complicated, let me know.
>
> Thanks so much!
>
> [Your Name]

**Event invitation (medium formality):**
> Dear Colleagues,
>
> Please join me for a working lunch this Wednesday 2/18 (noon, faculty lounge) where I'll be sharing what I think all of us need to be thinking about right now.
>
> [Body with context and stakes]
>
> Whether you're skeptical or curious (or both), this session is designed to give you a firsthand look at where things actually stand — not where the breathless headlines or clickbait social media say they stand.
>
> Faculty Lounge - 12:00pm - Lunch will be served.
>
> I hope you'll make it!
>
> Best,
>
> [Your Name]
