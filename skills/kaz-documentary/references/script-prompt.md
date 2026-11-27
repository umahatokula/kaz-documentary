# Script prompt template (for ChatGPT or another writer)

Fill the brackets from the episode's style choices, then give the user the prompt in a code block. Ask for web search to be on when the case has moved recently.

```
Use web search for this. Write a narration script for a YouTube documentary on the channel [CHANNEL], which investigates [CHANNEL REMIT].

TOPIC: [CASE, PLACE, DATE, ONE LINE ON WHAT HAPPENED].

LENGTH AND FORMAT
- About [WORDS FROM length] words of spoken narration, in [4-6] chapters.
- Mark each chapter on its own line: CHAPTER 1: [Title]. Everything else is plain narration paragraphs: no stage directions, music cues, bullet points or bracketed notes.
- Write for a text-to-speech voice: numbers and dates as words, no abbreviations except well-known ones, clear spoken sentences.
- OPENING: [from opening: "Open on the object at the centre: ..." / "Open on a close-up of a document: ..." / "Open on where the case stands today, then rewind." / "Open on one witness's account, in their reported words."]
- STRUCTURE: [from structure: "Tell it in time order." / "Start with the newest development (...), then go back to how it began." / "Follow one key piece of evidence (...) through the whole case." / "Set the official account against what the evidence shows, chapter by chapter."]
- [If perspective = yes:] Leave the end for me: finish the last chapter at the open questions, then write the single line [PERSPECTIVE] on its own. Do not write a verdict or a personal opinion.
- End with this exact final line: "Subscribe to [CHANNEL] for more on [CHANNEL REMIT]."

RULES
- Strictly fact-based. Use only verifiable facts from reliable sources (official reports, court and commission records, major news outlets). Do not invent quotes, dialogue, thoughts or scenes.
- Frame every allegation as an allegation, name its source, and include each denial or reason it is disputed.
- Non-graphic: describe deaths and injuries without gore.
- Neutral and serious; no sensational language.
- After the script, give a separate list of the key facts with a source link for each.
```

When the script comes back: trim it (cut sentences, keep the writer's wording), fact-check against sources, and fix what is wrong or unverifiable. Then draft the perspective segment (`references/perspective-guide.md`) where `[PERSPECTIVE]` stands.
