from crewai import Crew, LLM, Agent, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

from dotenv import load_dotenv
load_dotenv()

import json
import os

def trigger_crew():
    
    # Defining Tools
    # =============================================================================

    # Tool 1 - Configuring Gemini 2.0 Flash LLM
    llm = LLM(
        model="gemini/gemini-2.0-flash", # call model by provider/model_name
        temperature=0.8, # 0.8 is default
        api_key=os.getenv('GEMINI_API_KEY')
    )

    # Tool 2 - Serper API for Web Search
    search_tool = SerperDevTool(n_results=3)

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

    # source_credibility_expert = Agent(
    #     role = "Source Credibility Expert",
    #     goal = "To authoritatively assess the trustworthiness and historical reliability of a news source's domain based entirely on real-time web search results, synthesizing external evaluations and public perception.",
    #     backstory = '''
    #     You are an expert with over 12 years of dedicated experience in media forensics and dynamic online reputation assessment. Having historically navigated vast databases of media reliability, your current mandate is to leverage advanced search capabilities to dynamically ascertain a source's standing. 
    #     You meticulously craft search queries to expose a source's history of accuracy, any identified biases, and its general reputation across the web, relying on the collective intelligence of authoritative fact-checking organizations and media watchdogs. Your expertise lies in extracting and synthesizing 
    #     credible external evaluations to form a rapid and robust judgment on a source's trustworthiness.''',
    #     verbose = True, 
    #     tools=[search_tool],
    #     llm = llm 
    # )

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

    # Defining Tasks
    # =============================================================================

    content_analysis_master_task = Task(

        description='''

            Your primary task is to deeply analyze the provided news headline/topic - "{news_headline_or_topic}" and perform a deep web search using the "Serper Tool" to infer potential linguistic and stylistic indicators of misinformation, solely from search engine results. 
            Leveraging your expertise in interpreting search snippets and titles, this involves:

            1.  Initial Search Execution: Utilize the SerperDev Tool to conduct a broad search for the provided news headline or topic, aiming to gather a diverse set of top-ranking results (titles, snippets, URLs).
            2.  Inferred Sentiment Analysis: Analyze the language within the gathered search result titles and snippets to infer the overall emotional tone (positive, negative, neutral, mixed) and intensity. Look for disproportionate emotional loading or polarizing language in how the topic is presented across different sources.
            3.  Inferred Stylistic and Rhetorical Indicators: Based on the language in search snippets, identify inferred signs of:
                * Sensationalism: Use of hyperbole, exaggerated language, or clickbait-like phrasing in headlines or snippets.
                * Emotional Manipulation: Direct appeals to emotion instead of objective presentation across multiple snippet sources.
                * Overt Bias: Consistent use of loaded language or a skewed narrative appearing across a subset of snippets or specific source titles.
                * Unusual Language Patterns: Any linguistic choices in the snippets that deviate significantly from typical journalistic norms for a given subject.
            4.  Key Claim/Topic Identification (from snippets): Extract common keywords, entities, and the most prominent claims or assertions that consistently appear across the search result snippets, which represent the core "story" as perceived online.

            Your ultimate objective is to provide a preliminary inference of the article's likely content characteristics based on its public search appearance, without accessing its full text.''',

        expected_output='''

        A structured JSON object containing: 
        - 'inferred_sentiment': { 'overall_tone': 'positive'|'negative'|'neutral'|'mixed', 'intensity': 'low'|'medium'|'high' }
        - 'inferred_sensationalism_level': 'low'|'medium'|'high'\n- 'inferred_bias_indicators': { 'identified_extreme_phrases': ['phrase1', 'phrase2'], 'overall_inferred_strong_bias': true|false }
        - 'inferred_controversial_phrasing_detected': true|false\n- 'inferred_core_claims_keywords': ['keyword1', 'keyword2', 'claim_summary_from_snippet']"
        - 'inferred_unusual_language_patterns': ['pattern1', 'pattern2']\n- 'inferred_source_diversity': { 'source_count': 10, 'top_sources': ['source1.com', 'source2.com'] }

        ''',
        agent=content_analysis_master,
        # async_execution= True
    )

    # source_credibility_expert_task = Task(

    #     description='''

    #         As the Source Credibility Expert, your primary task is to infer the domain from a headline/query - {news_headline_or_topic} since a direct URL is unavailable, and meticulously assess its trustworthiness and historical reliability solely through real-time web searches. Leveraging your extensive experience in online reputation analysis, this involves:

    #         1.  Domain/Source Identification: Receive the domain name of the news source (e.g., from a URL provided by the user or extracted from search results from the Content Analysis Master).
    #         2.  Strategic Web Search Execution: Utilize the SerperDev Tool to craft and execute targeted Google search queries for the identified domain/source. Queries will specifically aim to uncover reputation, potential biases, and historical accuracy, e.g., "[domain name] credibility," "[domain name] bias," "is [domain name] reliable," "fact check [domain name] reviews," "who owns [domain name]".
    #         3.  Search Result Analysis and Synthesis: Systematically evaluate the top search results returned by the SerperDev Tool for the source. This comprehensive analysis includes:
    #             * Identifying direct mentions by established media watchdog organizations, independent fact-checking websites (e.g., Snopes, PolitiFact, Media Bias/Fact Check, NewsGuard), or reputable journalistic ethics bodies that offer explicit ratings or analyses.
    #             * Looking for common public perception or critical analyses regarding the source's reporting consistency, accuracy, history of retractions, or known editorial/political stances.
    #             * Reviewing "About Us" pages, Wikipedia entries, or industry profiles linked in search results for transparency, mission statements, and ownership information that might indicate bias or lack of journalistic standards.
    #             * Detecting widespread criticisms, legal actions, or repeated accusations of misinformation, propaganda, or a consistent partisan agenda.

    #         Your objective is to synthesize these real-time, externally-derived search findings into a swift yet authoritative judgment on the source's standing, providing crucial context for the overall veracity assessment.''',

    #     expected_output='''
    #        A structured JSON object containing: 
    #         - 'source_domain': (The extracted or inferred base domain, e.g., 'example.com')
    #         - 'credibility_rating': 'high'|'medium'|'low'|'fake'|'unknown'
    #         - 'reasoning_summary': (A concise string summarizing the key findings from the web search that led to the rating, e.g., 'Google search indicates frequent criticism for partisan bias on [domain].com', 'Multiple top results from fact-checking sites rate [domain].com as unreliable', 'Search results consistently show [domain].com as a reputable news organization', 'Insufficient verifiable information found for [domain].com via web search')
    #     ''',
    #     agent=source_credibility_expert,
    #     tools=[search_tool],
    #     # async_execution=True
    # )

    claim_verification_specialist_task = Task(

        description='''
            As the Claim Verification Specialist, your primary task is to receive a precise list of inferred factual claims or key topics (from the Content Analysis Master) and perform a real-time, comprehensive verification using dynamic web searches using "Serper Tool". Leveraging your expertise in advanced information retrieval and evidence synthesis, this involves:

            1.  Claim Ingestion: Accept the list of distinct factual claims or key topics directly provided by the Content Analysis Master.
            2.  Strategic Web Search Execution: For each received claim/topic, utilize the SerperDev Tool to craft and execute highly specific Google search queries designed to ascertain its veracity. Queries will be formulated to directly target factual confirmation or refutation, e.g., "is [claim text] true," "[claim text] debunked," "[claim text] fact check," "[claim text] scientific consensus."
            3.  Search Result Analysis and Evidence Synthesis: Systematically evaluate the top search results returned by the SerperDev Tool for each claim. This rigorous analysis includes:
                * Identifying direct answers or strong consensus among highly authoritative and reputable sources (e.g., academic institutions, government bodies, established news organizations known for accuracy, scientific journals).
                * Detecting explicit debunking or refutation by recognized fact-checking websites (e.g., Snopes, PolitiFact, FactCheck.org) or expert consensus statements.
                * Assessing the presence of significant counter-evidence, conflicting information from equally credible sources, or indicators of ongoing debate/lack of consensus.
                * Evaluating the recency and relevance of the information found in search snippets, prioritizing the most current and authoritative evidence.
            4.  Status Assignment: Based on the synthesis of web search findings and evidence confidence, assign a precise verification status to each claim:
                * 'verified': If multiple authoritative sources directly confirm the claim with high confidence.
                * 'debunked': If multiple authoritative sources or recognized fact-checkers explicitly refute or debunk the claim with high confidence.
                * 'unverifiable': If the web search yields insufficient direct evidence, conflicting information from credible sources, or no clear consensus to definitively confirm or refute the claim with high confidence.

            Your objective is to provide a swift and accurate initial assessment of the claims' veracity by cross-referencing them with external authoritative data, acting as a crucial filter against widespread factual inaccuracies.''',

        expected_output='''
         A structured JSON object containing a list of dictionaries, where each dictionary represents a claim and its verification status: 
         [ 
           { 
             'claim_text': 'Claim 1 text', 
             'verification_status': 'verified'|'debunked'|'unverifiable', 
             'reasoning_note': 'Confirmed by multiple authoritative sources via web search'|'Explicitly debunked by leading fact-checking sites via web search'|'Conflicting or insufficient evidence found via web search' 
            }, 
            { 
              'claim_text': 'Claim 2 text', 
              'verification_status': 'verified'|'debunked'|'unverifiable', 
              'reasoning_note': 'Confirmed by multiple authoritative sources via web search'|'Explicitly debunked by leading fact-checking sites via web search'|'Conflicting or insufficient evidence found via web search' 
            }
        ]''',
        tools=[search_tool],
        context=[content_analysis_master_task],
        agent=claim_verification_specialist
    )

    # Creating Crew
    # =============================================================================


    crew = Crew(
        agents=[content_analysis_master, claim_verification_specialist],
        tasks=[content_analysis_master_task, claim_verification_specialist_task],
        llm=llm,
        verbose=True
    )

    inputs = {
        "news_headline_or_topic" : "India to host G20 summit in 2025",
    }

    # Running the Crew
    result = crew.kickoff(inputs=inputs)

    print(result)