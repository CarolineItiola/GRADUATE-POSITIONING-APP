import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You help someone position what they have already
done against a specific opportunity.

You are given two things: what the person has done, in their own words,
and the opportunity they are aiming at.

RULES

Make claims only from what the person actually wrote. Every item in
your evidence list must quote their own words as its source. If you
cannot quote it, it is not evidence, it is a gap.

Never invent achievements, numbers, job titles or outcomes. If their
material contains no measurable result, put that in gaps rather than
supplying one.

Positioning is not flattery. It is the join between something they have
genuinely done and a problem the opportunity cares about. Where that
join is weak, say it is weak.

The next artefact must be one concrete thing they could build in a week
or less, with an output someone could look at. Not "network more" or
"improve your CV".

Reply with this JSON and nothing else:

{
  "positioning": "two or three sentences, addressed to them as you",
  "evidence": [
    {"claim": "what this shows", "their_words": "a short direct quote"}
  ],
  "gaps": ["what is missing that would make this stronger"],
  "next_artefact": "one concrete thing to build",
  "why_this_artefact": "one sentence on what it proves",
  "strength": "strong, partial or weak"
}

strength is your honest read of how well what they have matches what
the opportunity needs. Use weak when it barely connects.

Start your reply with { and end with }. No preamble, no markdown
fences, no reasoning in the reply itself.""" 


def get_positioning(what_i_have, the_opportunity, max_retries=3):
    question = (
        "WHAT I HAVE DONE:\n" + what_i_have
        + "\n\nTHE OPPORTUNITY:\n" + the_opportunity
    )

    for attempt in range(max_retries):
        response = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        raw = ""
        for block in response.content:
            if block.type == "text":
                raw += block.text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            print("Attempt", attempt + 1, "gave invalid JSON. Retrying.")
    return None


if __name__ == "__main__":
    have = """
CORE TECHNICAL SKILLS
Python (pandas, NumPy, scikit-learn, PyTorch, PySpark), SQL, EViews, Stata.
EDA pipelines, data validation, version control, reproducibility.
Logistic regression, classification and regression modelling, SVM, feature
engineering, class imbalance handling, model evaluation.
AI Engineering: JSON schema validation, Claude API, system prompts,
structured extraction output, Anthropic SDK, RAG pipelines, MCP, prompt
caching.
Statistics: hypothesis testing, regression analysis, time-series analysis,
quantitative modelling, econometric methods.
Tools: Claude Code, GitHub Codespaces, Lovable, React, TypeScript, Azure
Data Factory, Power BI, Bloomberg Terminal.

AI AND DATA PROJECTS

Multi-Source Price Feed Reconciliation Agent (Aug 2026)
Built an agent with the Claude API that reconciles conflicting price feeds
from three sources (Alpha Vantage, Finnhub, local warehouse), reasoning
about which feed to trust rather than averaging or defaulting to the last
trusted value. Modelled four source outcome states and judged staleness
against market open status, so blame is attributed correctly and closed
markets are not mistaken for broken feeds. Enforced an anti-averaging
invariant in Python code and wrote 27 invariant tests the agent cannot
violate, with every decision logged to a traceable audit trail.

Reliable Structured Chatbot with Prompt Caching (Jul 2026)
Built a live customer support chatbot for The AI Workshop handling student
enquiries across five intent categories. Implemented prompt caching to
reduce cost and response time, automatic retry logic, and a human handover
flag for questions the chatbot should not answer alone. Deployed on
Streamlit Cloud with secure API key handling, tested across 10 tricky
queries with all 10 handled correctly.

Clinical Document Extraction Pipeline (Jul 2026)
Built an NHS-style extraction pipeline using few-shot prompting and the
Claude API to convert unstructured patient notes into validated structured
JSON, with a schema validation loop and automatic retry logic.

WORK EXPERIENCE

The AI Workshop, London. AI Support Engineer. Jan 2026 to present.
Built and deployed a live production chatbot in Python with the Claude API
to triage student enquiries across five intent categories, with prompt
caching, retry logic, structured JSON responses and a human handover flag.
Provide customer support to students across the SQL and AI Bootcamp.

ALLReach Group UK, Peterborough. Data Engineer. Jan 2026 to Jul 2026.
Designed metadata-driven ingestion pipelines in Azure Data Factory
onboarding multiple source systems into a Delta Lake landing zone,
replacing hand-built per-source jobs with a single parameterised framework
and cutting new source onboarding from days to hours. Built Silver and Gold
transformation layers in Microsoft Fabric using PySpark, applying
idempotent incremental patterns so pipelines could be rerun safely.

Teaching Personnel, Hertfordshire. Mathematics Teacher. Sept 2025 to Aug 2026.
Delivered analytical curriculum across KS3 to KS5.

Gulf Treasures Limited, Lagos. Commodities and Equities Research Analyst.
Oct 2020 to Aug 2022. Conducted quantitative market research across
commodities, producing tailored client reports. Improved data sourcing
processes, increasing team productivity by 15%.

EDUCATION
MSc Finance and Investment Banking, University of Hertfordshire.
Distinction. Financial Data Analysis, Asset Valuation, Quantitative
Analysis, Financial Markets and Institutions.
BSc Economics, Federal University of Agriculture, Abeokuta. Second Upper.

SPEAKING AND COMMUNITY
Professional Member (MBCS), BCS. Speaker and facilitator, BCS London IT
Sovereignty Workshop, September 2026.
Coding Black Females. Delivered a workshop on building a production-ready
AI chatbot at the Global Tech Conference, September 2026.
"""

    opportunity = """AI engineering role at Gradient Labs. They build AI
support agents for financial services companies including Monzo and Wise.
Their pricing is outcomes-based with no platform fees: the client pays
only when the agent fully resolves a query on its own. When the agent
cannot resolve something it hands the conversation to the client's human
support team, and Gradient Labs earns nothing from that conversation.
They run 20 or more financial-services guardrails on every turn, covering
vulnerability, fraud, complaints and financial advice, and route low
confidence cases to a human by design. They are expanding into disputes,
lending, outbound and voice."""

    result = get_positioning(have, opportunity)

    if result:
        print("POSITIONING")
        print(result["positioning"])
        print()
        print("STRENGTH:", result["strength"])
        print()
        print("EVIDENCE")
        for e in result["evidence"]:
            print(" -", e["claim"])
            print("   \"" + e["their_words"] + "\"")
        print()
        print("GAPS")
        for g in result["gaps"]:
            print(" -", g)
        print()
        print("NEXT ARTEFACT")
        print(result["next_artefact"])
        print(result["why_this_artefact"])
    else:
        print("No valid response after 3 attempts.")