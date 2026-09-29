---
name: conversation-audio-longform
description: Turn raw interview or conversation audio into a chronology-faithful, speaker-labeled longform Markdown transcript. Use when a user wants transcription, light editing, privacy-aware publishing, or a polished conversational manuscript from recorded audio.
---

# Conversation Audio Longform

Create a readable publishable conversation from raw audio while keeping the source discussion recognizable. Fidelity to the recording takes priority over a clever rewrite or thematic summary.

## This project: 乱丢垃圾

Follow these repository conventions when this skill is used in this project:

- **Incoming recordings:** look in `audio/originals/`. Put new source recordings there, keep the original filename when practical, and never modify or move the source audio. Process only the files the user identifies; do not assume every file in the folder is in scope.
- **Speaker references:** the optional local clips are `audio/references/speaker_a.wav` and `audio/references/speaker_b.wav`. Keep labels anonymous as A/B unless the user provides names. Sending reference clips to a provider is an additional upload and may incur cost; only do so when the user has authorized that processing.
- **Provider and intermediate files:** check `TRANSCRIPTION.md` for this project's current provider instructions, local checks, output layout, and constraints. Use `transcribe_assemblyai.py` rather than inventing a separate pipeline. For each source recording, save the raw and diarized results under `transcripts/assemblyai/<recording-stem>/`; never overwrite an existing result or draft. Treat API submission as an external upload that may incur charges and require the user's authorization.
- **Publish manuscript:** save the edited longform as a new Markdown file in the same per-recording folder, named `<recording-stem>.publish-longform.md` (for example, `transcripts/assemblyai/乱丢垃圾 20260927 part 2/乱丢垃圾 20260927 part 2.publish-longform.md`). Preserve the raw and intermediate transcripts. If the folder or naming convention has changed, inspect the latest project files and follow the established convention.

## Workflow

1. **Locate and inspect the source.** Identify the requested audio files, duration, format, and any existing transcript or speaker references. Confirm which recording(s) the user wants processed. Keep original media unchanged.
2. **Transcribe with an authorized provider.** Reuse the provider the user chose or already configured. For Chinese-English code-switched conversations, AssemblyAI Universal-3.5 Pro is a suitable option when the user has an account/key; request native multilingual transcription, diarization, and the expected speaker count, with a short context prompt when useful. Verify current parameter names against provider documentation. Do not upload audio unless the user authorized external processing. Never print or expose API keys. If network access is blocked, request the required permission once. Record the provider job ID before polling so a save or formatting failure can recover the completed job without re-uploading or duplicate charges.
3. **Keep transcript stages separate.** Preserve the raw provider response and a readable diarized transcript as separate files. Create the publish draft as a new Markdown output. Do not overwrite source audio, raw results, or prior drafts unless asked.
4. **Edit from the transcript in chronological order.** Use timestamps and speaker-tagged utterances as the source of truth. Preserve the order in which ideas, examples, questions, disagreements, and revisions occur. Do not turn the discussion into a thematic summary, invent prompts or replies, move ideas to improve an essay arc, or change who said what. Consolidate adjacent short utterances only when the turn remains clear; keep meaningful interruptions, jokes, tangents, and returns to the main topic.
5. **Polish without flattening the voices.** Remove mechanical ASR spacing, false starts, repeated filler, and verbal clutter where they do not carry meaning. Repair names, terminology, and English spelling only when the audio/context makes the correction clear. Preserve natural code-switching, colloquial phrasing, uncertainty, humor, and each speaker's distinct way of thinking. Prefer concise spoken language over formal prose. If a substantive phrase remains unclear, do not guess: omit only if nonessential; otherwise leave a discreet editorial marker or ask the user to review it.
6. **Apply the user's privacy direction.** When publishing is intended, inspect for personally identifying or sensitive details. Generalize or remove coworker names, client/patient information, internal project/product names, employer-sensitive details, private hiring discussions, and identifying plans when they are not essential to the conversation. Keep public names and ordinary first-person opinions when they do not identify someone or reveal sensitive information. Do not silently remove a major example; generalize it while retaining its point where possible.
7. **Honor style references at the level of traits.** If asked to evoke named living creators, do not imitate their exact voice. Translate the request into high-level traits (for example, loose long-form exchange, curious follow-ups, candid humor, philosophical detours) and apply those while retaining the recorded speakers' own voices.
8. **Review before delivery.** Compare the publish draft against the time-coded source, especially after long monologues and speaker changes. Check chronology, speaker labels, factual names, missing examples, privacy edits, and that the draft is still a conversation rather than a summary. Keep anonymous labels such as A/B unless the user supplies publishable names.

## Output

Create one separate `.md` publish draft with a clear title, optional one-line deck, and readable speaker labels. Use substantial paragraphs that preserve conversational rhythm; avoid both line-by-line transcript clutter and over-compressed blocks that erase the back-and-forth. Retain original and intermediate files. Report the output path and briefly disclose any material redactions or unresolved audio ambiguities.
