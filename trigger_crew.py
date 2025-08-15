from crewai import Crew, LLM, Agent, Task
from crewai_tools import SerperDevTool

from dotenv import load_dotenv
load_dotenv()

import json
import os
import re 

import time 

def extract_json_from_markdown(text: str):

    json_block_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    parsed_json = {}
    matches = json_block_pattern.findall(text)

    if matches:
        try:
            # Attempt to parse the first match as JSON
            parsed_json = json.loads(matches[0])

        except json.JSONDecodeError:
            print("Failed to decode JSON from the provided text.")

    return parsed_json

def fact_check_crew(news_headline_or_topic):

    start_time = time.time() # Start timing the execution

    llm_api_key = os.getenv('GEMINI_API_KEY') # SET your Desired LLM API Key in .env file as <PROVIDER_API_KEY> (e.g., GEMINI_API_KEY, OPENAI_API_KEY, etc.)

    if not llm_api_key:
        raise ValueError("LLM_API_KEY environment variable is not set in the .env file. Please set it to your desired LLM API key.")
    
    # Defining Tools
    # =============================================================================

    # Tool 1 - Configuring Gemini 2.0 Flash LLM
    llm = LLM(
        model="gemini/gemini-2.0-flash", # call model by provider/model_name
        temperature=0.8, # 0.8 is default
        api_key=llm_api_key, # Set your LLM API Key here
    )

    # Tool 2 - Serper API for Web Search
    search_tool = SerperDevTool(n_results=3) # Increased results for better analysis

    # Defining Agents
    # =============================================================================

    content_analysis_master = Agent(
        role = "Content Analysis Master",
        goal = "To infer potential signs of sensationalism, extreme framing, or unusual language associated with a news headline or topic, based solely on how it is presented in web search results. This agent identifies initial red flags from public search visibility.",
        backstory = '''
        You are an expert with over a decade of experience specializing in the subtle art of linguistic forensics, now highly adept at extracting meaningful signals from search engine snippets. Having processed trillions of words and observed how misinformation manifests online,
        your refined algorithms can infer characteristic patterns of sensationalism, emotional manipulation, or biased framing even when direct article text is inaccessible. You discern "red flags" by analyzing how a news piece is presented across various search results, identifying
        language, tone, and claim types that deviate from standard, objective reporting. Your expertise is in deriving powerful initial insights from limited textual exposure.''',
        verbose = True,
        tools=[search_tool],
        llm = llm
    )

    claim_verification_specialist = Agent(
        role = "Claim Verification Specialist",
        goal = "To perform real-time, authoritative verification of specific factual claims by cross-referencing them against external data obtained through targeted web searches.",
        backstory = '''
        You are an expert with 8 years of focused experience in advanced information triage and dynamic information validation. Having historically refined your methods for identifying high-prevalence falsehoods, your current mandate is to leverage comprehensive search capabilities to rapidly confirm or
        refute specific assertions. You meticulously formulate queries to solicit direct factual answers, identify consensus among authoritative sources, or uncover explicit debunkings from the vast expanse of the internet. Your expertise lies in efficiently and accurately assessing the veracity of claims
        by consulting the most reliable external data available.''',
        verbose = True,
        tools=[search_tool],
        llm = llm
    )

    final_verdict_synthesizer = Agent(
        role = "Final Verdict Synthesizer",
        goal = "To consolidate all analytical insights, render a definitive verdict on the news item's authenticity, provide supporting citations, quantify sources checked, and offer a clear recommendation.",
        backstory = '''
        You are a seasoned expert in strategic communication and evidence synthesis, possessing years of experience in distilling complex analytical reports into clear, actionable intelligence. Your forte is integrating disparate data points from specialized analyses to construct a comprehensive, authoritative conclusion. You are adept at identifying the critical evidence needed to support a verdict, meticulously tracking sources, and crafting concise, practical recommendations for decision-makers. You excel at summarizing complex findings into an easily digestible format for end-users.''',
        verbose = True,
        llm = llm
    )


    # Defining Tasks
    # =============================================================================
    
    content_analysis_master_task = Task(
        description='''
            Your **absolute first and foremost task** is to determine the factual accuracy of the **exact news headline/topic provided by the user: "{news_headline_or_topic}"**.

            Perform highly targeted web searches using "Serper Tool" for this *exact phrase* (e.g., "{news_headline_or_topic} fact check", "{news_headline_or_topic} debunked", "{news_headline_or_topic} true or false").

            Based on these direct searches:

            1.  **Evaluate Input Headline's Veracity:** Is the claim in "{news_headline_or_topic}" directly confirmed as true, explicitly debunked as false, or is its veracity unclear from reputable sources?
            2.  **Identify Correct Counter-Information (if applicable):** If the input headline is found to be false or misleading, you *must* identify the precise factual information that contradicts it (e.g., "The G20 summit in 2025 will be hosted by South Africa, not India.") and provide a primary source for this correct information. If the input is true, state 'N/A' for this field.
            3.  **Collect Supporting URLs:** Gather all relevant URLs that either confirm or debunk the input headline, and any URLs that provide the correct counter-information.

            After this primary verification, secondarily infer linguistic indicators:
            4.  **Inferred Linguistic Analysis:** Analyze general search results for "{news_headline_or_topic}" to infer overall sentiment (tone), sensationalism, hyperbole, clickbait-like phrasing, overt bias, or extreme framing.
            5.  **Key Claim/Topic Identification:** Extract prominent claims or keywords from snippets that are central to the overall story, which may or may not be identical to the input headline, but contribute to its context.

            Your output must be a structured JSON object reflecting this direct verification and contextual analysis.
            ''',
        expected_output='''
        A structured JSON object containing:
        {
            'input_headline_direct_verification_status': 'verified'|'debunked'|'unverifiable',
            'correct_information_if_debunked': 'The correct information is X, supported by Y.com' | 'N/A' (if verified or unverifiable),
            'supporting_urls_for_input_verification': [{'title': 'Direct Source Title', 'link': 'http://directsource.com'}],
            'inferred_sentiment': { 'overall_tone': 'positive'|'negative'|'neutral'|'mixed', 'intensity': 'low'|'medium'|'high' },
            'inferred_sensationalism_level': 'low'|'medium'|'high',
            'inferred_bias_indicators': { 'identified_extreme_phrases': ['phrase1', 'phrase2'], 'overall_inferred_strong_bias': true|false },
            'inferred_controversial_phrasing_detected': true|false,
            'inferred_core_claims_keywords': ['keyword1', 'keyword2', 'claim_summary_from_snippet']
        }
        ''',
        agent=content_analysis_master
    )

    claim_verification_specialist_task = Task(
        description='''
            As the Claim Verification Specialist, your primary task is to receive a precise list of inferred factual claims or key topics (from the Content Analysis Master's output) and perform a real-time, comprehensive verification using dynamic web searches using "Serper Tool". Leveraging your expertise in advanced information retrieval and evidence synthesis, this involves:

            1.  Claim Ingestion: Accept the list of distinct factual claims or key topics directly provided by the Content Analysis Master.
            2.  Strategic Web Search Execution: For each received claim/topic, utilize the SerperDev Tool to craft and execute highly specific Google search queries designed to ascertain its veracity. Queries will be formulated to directly target factual confirmation or refutation, e.g., "is [claim text] true," "[claim text] debunked," "[claim text] fact check," "[claim text] scientific consensus." Capture the URLs of the sources found for each claim.
            3.  Search Result Analysis and Evidence Synthesis: Systematically evaluate the top search results returned by the SerperDev Tool for each claim. This rigorous analysis includes:
                * Identifying direct answers or strong consensus among highly authoritative and reputable sources (e.g., academic institutions, government bodies, established news organizations known for accuracy, scientific journals).
                * Detecting explicit debunking or refutation by recognized fact-checking websites (e.g., Snopes, PolitiFact, FactCheck.org) or expert consensus statements.
                * Assessing the presence of significant counter-evidence, conflicting information from equally credible sources, or indicators of ongoing debate/lack of consensus.
                * Evaluating the recency and relevance of the information found in search snippets, prioritizing the most current and authoritative evidence.
            4.  Status Assignment: Based on the synthesis of web search findings and evidence confidence, assign a precise verification status to each claim:
                * 'verified': If multiple authoritative sources directly confirm the claim with high confidence.
                * 'debunked': If multiple authoritative sources or recognized fact-checkers explicitly refute or debunk the claim with high confidence.
                * 'unverifiable': If the web search yields insufficient direct evidence, conflicting information from equally credible sources, or no clear consensus to definitively confirm or refute the claim with high confidence.

            Your objective is to provide a swift and accurate initial assessment of the claims' veracity by cross-referencing them with external authoritative data, acting as a crucial filter against widespread factual inaccuracies.
            Output a comprehensive list of claims with their verification status and detailed reasoning, including the URLs of the most relevant sources found for each claim.
            ''',
        expected_output='''
            A structured JSON object containing a list of dictionaries, where each dictionary represents a claim and its verification status, AND a consolidated list of all unique URLs consulted during the verification process:
            {
            "claims_verified_details": [
                {
                'claim_text': 'Claim 1 text',
                'verification_status': 'verified'|'debunked'|'unverifiable',
                'reasoning_note': 'Confirmed by multiple authoritative sources via web search',
                'supporting_urls': ['http://source1.com/claim1', 'http://source2.com/claim1']
                },
                {
                'claim_text': 'Claim 2 text',
                'verification_status': 'verified'|'debunked'|'unverifiable',
                'reasoning_note': 'Explicitly debunked by leading fact-checking sites via web search',
                'supporting_urls': ['http://debunking_site.org/claim2']
                }
            ],
            "all_verification_sources_consulted": [
                {'title': 'Source Title 1', 'link': 'http://source1.com/claim1'},
                {'title': 'Source Title 2', 'link': 'http://debunking_site.org/claim2'}
            ]
            }''',
        tools=[search_tool],
        context=[content_analysis_master_task], # This provides the output of the content_analysis_master_task to this task
        agent=claim_verification_specialist
    )

    final_verdict_task = Task(
        description="""
            Your final task is to synthesize all analytical insights to provide a comprehensive, actionable verdict on the news item, **explicitly and primarily addressing the veracity of the user's original input headline: "{news_headline_or_topic}"**.

            Instructions:
            1.  Core Verdict Determination (Highest Priority):
                * If 'input_headline_direct_verification_status' is 'debunked'**: The `final_verdict` **MUST be "Fake"**. The `verdict_reasoning` must clearly state that the input claim is false and provide the 'correct_information_if_debunked' from the Content Analysis Master.
                * If 'input_headline_direct_verification_status' is 'verified'**:
                    * If 'inferred_sensationalism_level' is 'high' OR 'overall_inferred_strong_bias' is true: "Likely Verified" (suggesting caution despite factual accuracy).
                    * Otherwise: "Verified".
                * If 'input_headline_direct_verification_status' is 'unverifiable'**: "Uncertain". The reasoning should state the lack of definitive evidence.

            2.  Comprehensive Reasoning: Elaborate on the `verdict_reasoning` by incorporating relevant insights from linguistic analysis (sentiment, sensationalism, bias) and the `claims_verified_details` from the Claim Verification Specialist.

            3.  Compile Supporting Citations: Consolidate ALL unique URLs from 'supporting_urls_for_input_verification' (from Content Analysis) and 'all_verification_sources_consulted' (from Claim Verification). Present them clearly, with their titles where available. Remove duplicates.

            4.  Count Sources: Calculate the total number of unique URLs (sources) compiled.

            5.  Formulate Recommendation: Provide a clear, concise recommendation directly tied to the `final_verdict`.
                * If "Fake": "AVOID SHARING THIS CONTENT. The original claim is false. The correct information is: [insert correct_information_if_debunked here]."
                * If "Verified": "This information appears reliable and can be shared."
                * If "Likely Verified": "This information appears largely reliable, but contains some sensationalism/bias. Share with mild caution."
                * If "Uncertain": "Proceed with caution. The veracity of this information could not be definitively determined. Seek additional reputable sources."

            Output a structured JSON object containing all these elements.
            """,
        expected_output="""
        A structured JSON object containing:
        {
          "final_verdict": "Verified" | "Likely Verified" | "Uncertain" | "Likely Fake" | "Fake",
          "verdict_reasoning": "A concise explanation of why this verdict was reached, primarily focused on the original input headline's veracity. If 'Fake', it *must* state the input claim is false and provide the correct information.",
          "supporting_citations": [
            {"title": "Source Title 1", "url": "http://source1.com"},
            {"title": "Source Title 2", "url": "http://source2.com"}
          ],
          "total_sources_checked": 15,
          "recommendation": "A clear recommendation for the user (e.g., 'AVOID SHARING THIS CONTENT. The original claim is false. The correct information is: X.', 'This information appears reliable and can be shared.')"
        }
        """,
        agent=final_verdict_synthesizer,
        context=[content_analysis_master_task, claim_verification_specialist_task]
    )

    # Creating Crew
    # =============================================================================

    crew = Crew(
        agents=[content_analysis_master, claim_verification_specialist, final_verdict_synthesizer], # Add the new agent
        tasks=[content_analysis_master_task, claim_verification_specialist_task, final_verdict_task], # Add the new task
        llm=llm,
        verbose=True
    )

    inputs = {
        "news_headline_or_topic" : news_headline_or_topic,
    }

    # Running the Crew
    result = crew.kickoff(inputs=inputs)

    # Extracting the final report from the result
    final_report = extract_json_from_markdown(result.raw)

    end_time = time.time() # End timing the execution
    execution_time = end_time - start_time

    return final_report