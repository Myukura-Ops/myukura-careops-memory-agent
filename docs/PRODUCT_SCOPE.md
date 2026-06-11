# Product Scope

## What is MyuKura CareOps Memory Agent?
A supervised operational memory agent for clinical teams that converts approved synthetic clinical notes into reviewable operational tasks, handoffs and audit trails.

## Problem
Clinical teams spend hours manually processing notes into tasks, scheduling, and handoff summaries, leading to burnout and operational delays.

## Solution
An agentic system that ingests synthetic clinical notes, uses tools to verify state, and outputs proposed tasks and summaries for human review before any operational action is finalized.

## Users
Clinical coordinators, nurses, and medical administrative staff (simulated personas).

## MVP Features
- Ingestion of synthetic notes.
- Agent analysis using Gemini.
- Task extraction and handoff generation.
- Human-in-the-loop task board for approval.
- MongoDB-backed state and audit trails.

## Out of Scope
- **No diagnosis**
- **No treatment recommendations**
- **No real patient data**
- **No real EHR integrations**
- **No direct WhatsApp/Email delivery** in the MVP.
