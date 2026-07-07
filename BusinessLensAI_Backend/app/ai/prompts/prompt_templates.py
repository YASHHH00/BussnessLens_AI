"""
BusinessLens AI — AI Prompt Templates

All prompts are centralized here. Prompts are built using string templates
with explicit field vocabularies injected from BusinessFieldRegistry.

Critical security rule enforced in every prompt:
  FORBIDDEN: Generating SQL statements.
  REASON: SQL is generated exclusively by the Analytics Engine using
          allow-listed identifiers. AI only produces structured JSON.
"""

from __future__ import annotations

from typing import Any


# ------------------------------------------------------------------ #
# Schema Analysis Prompt
# ------------------------------------------------------------------ #

SCHEMA_ANALYSIS_SYSTEM = """You are a Business Intelligence schema analyst.
Your task is to analyze database table and column metadata and map physical columns
to standardized business fields.

CRITICAL RULES:
1. DO NOT generate any SQL statements under any circumstances.
2. Return ONLY valid JSON matching the specified schema.
3. Base your analysis ONLY on column names, data types, sample values, and business context.
4. Confidence scores must be between 0.0 and 1.0.
5. Never invent business fields that are not in the provided vocabulary.
6. If no match is found, return "business_field": null for that column."""


def build_schema_analysis_prompt(
    tables_json: dict[str, Any],
    field_vocabulary: list[dict],
    domain_context: dict[str, Any],
) -> str:
    """
    Build the schema analysis prompt.
    Injects full table/column metadata and the registered field vocabulary.
    """
    import json

    # Compact table representation (no sample values in main prompt — reduces tokens)
    compact_tables = {}
    for table_name, table_data in tables_json.items():
        compact_tables[table_name] = {
            "row_count": table_data.get("row_count"),
            "columns": [
                {
                    "name": c["name"],
                    "type": c.get("physical_type"),
                    "nullable": c.get("nullable"),
                    "sample_values": c.get("sample_values", [])[:3],  # max 3 samples
                }
                for c in table_data.get("columns", [])
            ],
        }

    return f"""Analyze the following database schema and map each column to a business field.

## Domain Context
{json.dumps(domain_context, indent=2)}

## Database Schema
{json.dumps(compact_tables, indent=2)}

## Available Business Fields (ONLY use these — do not invent new ones)
{json.dumps(field_vocabulary, indent=2)}

## Required Output Format (JSON)
Return a JSON object with this exact structure:
{{
  "table_analyses": {{
    "<table_name>": {{
      "purpose": "<one sentence describing what this table stores>",
      "columns": [
        {{
          "column_name": "<physical column name>",
          "business_field": "<business field name from vocabulary, or null if no match>",
          "confidence": <float 0.0-1.0>,
          "reasoning": "<brief explanation of why this mapping was chosen>",
          "is_primary_key": <boolean>,
          "data_quality_note": "<optional note about data quality from sample values>"
        }}
      ]
    }}
  }},
  "suggested_primary_table": "<table_name most likely to be the primary fact table>",
  "join_hints": [
    {{
      "from_table": "<table>",
      "from_column": "<column>",
      "to_table": "<table>",
      "to_column": "<column>",
      "relationship": "many-to-one | one-to-many | one-to-one"
    }}
  ],
  "domain_fit_score": <float 0.0-1.0, how well the schema fits the declared domain>,
  "analyst_notes": "<overall notes about the schema quality and mapping confidence>"
}}

Analyze now:"""


# ------------------------------------------------------------------ #
# Mapping Suggestion Prompt
# ------------------------------------------------------------------ #

MAPPING_SUGGESTION_SYSTEM = """You are helping a business analyst map database columns
to standard business field names. Review the proposed mappings and suggest improvements.
DO NOT generate SQL. Return ONLY valid JSON."""


def build_mapping_suggestion_prompt(
    unmapped_columns: list[dict],
    field_vocabulary: list[dict],
    existing_mappings: list[dict],
) -> str:
    import json
    return f"""Review these unmapped database columns and suggest business field mappings.

## Already Mapped Columns (for context — do not re-suggest these)
{json.dumps(existing_mappings, indent=2)}

## Unmapped Columns (suggest mappings for these)
{json.dumps(unmapped_columns, indent=2)}

## Available Business Fields
{json.dumps(field_vocabulary, indent=2)}

Return JSON:
{{
  "suggestions": [
    {{
      "column_name": "<physical column name>",
      "table_name": "<table name>",
      "business_field": "<field name or null>",
      "confidence": <0.0-1.0>,
      "alternative_fields": ["<alt1>", "<alt2>"],
      "reasoning": "<brief explanation>"
    }}
  ]
}}"""


# ------------------------------------------------------------------ #
# Insight Phrasing Prompt
# ------------------------------------------------------------------ #

INSIGHT_PHRASING_SYSTEM = """You are a business analyst writing executive-level insights.
Convert numeric KPI results into clear, actionable business language.
DO NOT generate SQL. Return ONLY valid JSON."""


def build_insight_phrasing_prompt(
    kpi_results: list[dict],
    rule_triggers: list[dict],
    domain_context: dict,
    date_range: str,
) -> str:
    import json
    return f"""Convert these analytics results into business insights.

## Period: {date_range}
## Domain: {domain_context.get("domain", "Retail")}

## KPI Results
{json.dumps(kpi_results, indent=2)}

## Business Rules Triggered
{json.dumps(rule_triggers, indent=2)}

Return JSON:
{{
  "insights": [
    {{
      "title": "<short headline>",
      "body": "<2-3 sentence explanation for a business audience>",
      "severity": "critical | warning | info | positive",
      "metric": "<KPI or rule name>",
      "recommended_action": "<optional: what to do about this>",
      "confidence": <0.0-1.0>
    }}
  ],
  "executive_summary": "<3-4 sentence overall period summary>"
}}"""


# ------------------------------------------------------------------ #
# Smart Mapping Memory Prompt
# ------------------------------------------------------------------ #

SMART_MEMORY_SYSTEM = """You are helping recall and refine business field mappings
based on historical mapping patterns and current schema similarity.
DO NOT generate SQL. Return ONLY valid JSON."""


def build_smart_memory_prompt(
    current_schema_columns: list[dict],
    historical_mappings: list[dict],
    field_vocabulary: list[dict],
) -> str:
    import json
    return f"""Based on historical mapping patterns, suggest mappings for the current schema.

## Historical Successful Mappings (from previous connections)
{json.dumps(historical_mappings[:20], indent=2)}

## Current Schema Columns (need mapping suggestions)
{json.dumps(current_schema_columns, indent=2)}

## Available Business Fields
{json.dumps(field_vocabulary, indent=2)}

Return JSON:
{{
  "suggestions": [
    {{
      "column_name": "<column>",
      "table_name": "<table>",
      "business_field": "<field or null>",
      "confidence": <0.0-1.0>,
      "source": "historical_match | vocabulary_match | inference",
      "reasoning": "<why this mapping was suggested>"
    }}
  ]
}}"""


# ------------------------------------------------------------------ #
# AI Business Assistant Prompt
# ------------------------------------------------------------------ #

ASSISTANT_SYSTEM = """You are BusinessLens AI Assistant, a specialized AI Business Analyst.
Your role is to answer natural language questions about the user's business metrics.

CRITICAL RULES:
1. DO NOT generate raw SQL queries under any circumstances.
2. Return ONLY valid JSON matching the specified structure.
3. Translate user questions into structured AnalyticsQueryRequest parameters using the provided business vocabulary.
4. If data is provided in the prompt context, synthesize executive answers directly citing the metrics."""


def build_assistant_prompt(
    question: str,
    field_vocabulary: list[dict],
    recent_kpi_summary: list[dict],
    conversation_history: list[dict],
) -> str:
    import json
    return f"""Answer the user's business question or translate it into a structured query request.

## Available Business Fields Vocabulary
{json.dumps(field_vocabulary, indent=2)}

## Recent KPI Summary Context
{json.dumps(recent_kpi_summary, indent=2)}

## Conversation History
{json.dumps(conversation_history[-5:], indent=2)}

## User Question
"{question}"

Return JSON matching this exact structure:
{{
  "intent": "answer | query | clarification",
  "narrative_response": "<executive natural language answer citing KPI data if intent is 'answer'>",
  "suggested_query": {{
    "metrics": ["<metric field name>"],
    "dimensions": ["<dimension field name>"],
    "filters": [],
    "date_range_field": "<date field or null>",
    "time_grain": "<day | week | month | quarter | year | null>",
    "limit": 50
  }},
  "follow_up_questions": ["<suggested relevant follow-up question 1>", "<suggested follow-up 2>"]
}}"""
