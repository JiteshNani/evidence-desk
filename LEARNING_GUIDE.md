# Learn Evidence Desk

This is an AI-assisted portfolio project created on 14 October 2026. Before describing it as your own engineering expertise in an interview, run it, read every function and complete the exercise below. Use “portfolio prototype” rather than “production experience.”

## Three learning sessions

1. **Run and inspect (45 minutes):** create the environment, run tests and the evaluation, compare the saved report, try one successful and one invalid API request.
2. **Trace the design (60 minutes):** start from the endpoint, follow validation into the core, draw the data flow and explain where parameters are fitted and where evaluation data enters.
3. **Change and defend (90 minutes):** implement the exercise, add a regression test, rerun evaluation and write down one result that worsened.

## Design questions

- Why combine sparse retrieval methods, and what does rank fusion lose?
- How would you create a larger held-out evaluation set without leakage?
- When is abstention too conservative?
- What changes are needed for multi-user document authorization?

## Practical exercise

Add ten paraphrased questions and ten unanswerable questions without changing thresholds. Report failures separately. Then replace lexical retrieval with a separately measured embedding baseline, retaining exact citation validation.

## A truthful interview introduction

“This is a recent AI-assisted portfolio prototype. It demonstrates documents → word chunks → tf-idf and bm25 → rank fusion → coverage gate → quoted answer. I can show the implementation and evaluation, and I distinguish its small demo results from operational performance.”

## Readiness check

Explain the baseline, identify two failure cases, change one behavior without assistance, write a test that fails before your fix, and explain why the reported numbers are limited. Record your learning and changes in a new commit; never backdate the project.
