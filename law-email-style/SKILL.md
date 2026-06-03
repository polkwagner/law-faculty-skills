---
name: law-email-style
description: Draft emails, memos, and messages in your voice. Use when asked to draft, write, or compose any email or professional communication.
license: CC-BY-4.0
metadata:
  author: "[Your Name]"
---

# Law Email Style Guide

Use this guide for email-specific formatting. Voice, tone, banned phrases, and preferred expressions are defined in the **Writing & Tone** section of CLAUDE.md — that baseline always applies. This skill adds email-specific structure on top.

## Voice Priorities (apply to every email)

These three rules are the most frequently violated in drafts. Apply them before anything else:

1. **Use contractions freely.** Even in semi-formal emails to faculty, deans, and external correspondents, [Your Name] uses "I'm", "we're", "can't", "won't", "it's", "that's", "let's", "don't", "I'd", "you'll". Drafts without contractions read as stiff and are wrong. Every email should contain at least one natural contraction.
2. **Never open with a preamble.** Do not start the first sentence (after the greeting) with "Thanks for reaching out", "I wanted to reach out", "I hope this email finds you well", "Thanks for your email", "Great question", "Absolutely", or "I'd be happy to help". Open with the substance directly.
3. **At most 1–2 em-dashes per email, regardless of length.** [Your Name] prefers commas for asides. Em-dashes are reserved for strong emphasis or to set off lists containing commas. Never use em-dashes as bullet leaders.

## Agent Dependencies

This skill dispatches sub-agents for pre-send quality checks. Each call is guarded — the email still produces without them, but factual and style verification are weaker.

- `factual-reviewer` — extracts discrete factual claims for verification.
- `fact-verifier` — live web/source verification of specific claims.
- `voice-style-checker` — voice, style, and AI-tell scan.

Install from the `agents/` directory of this skill's repo into `~/.claude/agents/`.

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
- Bullet characters (•) for bullet lists, never em-dashes as bullet leaders.
- Numbered lists for sequential action items, deadlines, or options.
- "So," as a casual transition between sections.
- Run the AI Writing Tell Check (see CLAUDE.md) before sending. Applies to emails too.
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
