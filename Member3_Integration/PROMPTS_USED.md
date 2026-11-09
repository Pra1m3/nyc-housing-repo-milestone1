# Prompts and AI assistance disclosure

## User prompt used for this handoff (verbatim)

> hey chat this is my data enginnering project im in a team of 4 and im about to send you member 1's work and also what each member should do im member 4 however i want us to also do members 2 and 3's work since they are running late and its not prohibited to do other memebrs is work they will just get a deduction so i want us to first do member's 2 and 3 work and then well go from there before we start i want you thoroughly go over the description and members 1 work and then start doing here is what you need to do so act as senior data engineer and finish memeber 2 and 3's work and give me each one as seerate zip file

## Role requirements appended by the user

Member 1: Housing data lead
- Choose the housing dataset, with the feasibility check if it's outside the catalog.
- EDA and pre-integration cleaning for housing: missing values, outliers (IQR or domain rules), duplicates, and standardizing dates, strings and geographic IDs.
- Create the GitHub repo and own the README setup steps.
- 2 research questions + 2 charts.

Member 2: Transportation data lead
- Choose the transportation dataset (if it's very large, justify the filtered sample).
- The same EDA and pre-integration cleaning for the transport data.
- Aggregate to the common level (e.g., ZIP/borough × year).
- 2 research questions + 2 charts.

Member 3: Integration and notebook lead
- Decide the join key and granularity with Members 1 and 2, and document the justification.
- Perform the integration and the required post-integration cleaning: new nulls from the join, redundant columns, dtype mismatches.
- Assemble the final notebook (markdown narrative, dataset links, the prompts-used section) and keep the contribution table.
- 2 research questions + 2 charts.

Member 4: Website and deployment lead
- Build the Dash (or other) app skeleton: layout, dropdown filters, search mode (parse text like "Brooklyn 2022 new buildings" into filters), and the central **Generate Report** button wired to all charts.
- Deploy on Render or Vercel, test it, and write the README deployment section.
- Write the final submission email.
- 2 research questions + 2 charts.

## Assistance actually used

Codex/OpenAI assisted with reading the supplied requirements and original notebook, inspecting official source metadata, downloading full snapshots, selecting a coverage-aware join, writing the cleaning/integration code, research questions, charts, narrative, tests and packaging. No synthetic records or invented findings were used. The four findings were calculated from the included snapshots. No separate subagent prompts were used. Tool calls were used to inspect files, fetch source data and execute/validate code; they are implementation steps, not additional research questions.

The supplied Member 1 notebook contains no prompt log; its earlier prompts are unknown and must be added by its original contributor if applicable. Names/student IDs were not supplied. Do not replace this disclosure with a claim that Members 2/3 independently authored the work.
