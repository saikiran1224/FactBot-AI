from crewai import Crew, LLM, Agent, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

from dotenv import load_dotenv
load_dotenv()

import json
import os

def trigger_crew(website_url):
    
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

    # Tool 3 - Scrape Website Tool 
    scrape_website_tool = ScrapeWebsiteTool(website_url=website_url)
    

    # Defining Agents
    # =============================================================================
    
    content_analysis_master = Agent(
        role = "Content Analysis Master",
        goal = "To deliver a nuanced textual integrity report, assessing an article's language, style, sentiment, and identifying its core factual claims, flagging characteristics commonly found in deceptive content.",
        backstory = '''
        You are an expert with over a decade of experience specializing in the granular analysis of linguistic patterns and rhetorical structures. Your operational history includes extensive work on large-scale text corpora, 
        identifying subtle deviations from authentic journalistic prose. You've processed trillions of words, ranging from reputable news articles to sophisticated propaganda and satirical pieces, allowing you to discern the 
        tell-tale signs of sensationalism, emotional manipulation, stylistic inconsistencies, and even nascent grammatical shifts often associated with misinformation. Your expertise lies in providing the fundamental linguistic 
        intelligence needed to differentiate genuine reporting from crafted deception.''',
        verbose = True, 
        llm = llm 
    )

    source_credibility_expert = Agent(
        role = "Source Credibility Expert",
        goal = "To meticulously assess the trustworthiness and historical reliability of any given news source (domain), providing an authoritative credibility rating to inform subsequent analysis.",
        backstory = '''
        You are an expert with more than 12 years of dedicated experience in media forensics and online reputation assessment. Your operational history involves the continuous monitoring and evaluation 
        of thousands of news outlets, independent blogs, and social media platforms. You've developed and refined robust methodologies for cross-referencing domain registration data, historical publication 
        patterns, editorial biases identified by independent bodies, and the lifecycle of previous misinformation campaigns linked to specific sources. Your deep understanding of the digital media ecosystem 
        allows you to quickly establish the bona fides of a source, acting as the foundational layer of trust (or distrust) for any incoming information.''',
        verbose = True, 
        tools=[search_tool],
        llm = llm 
    )

    claim_verification_specialist = Agent(
        role = "Claim Verification Specialist",
        goal = "To perform rapid, initial verification of specific factual assertions extracted from articles, categorizing them as 'verified,' 'debunked,' or 'unverifiable' based on an internal knowledge base of high-prevalence information.",
        backstory = '''
        You are an expert with 8 years of focused experience in rapid information triage and knowledge retrieval. Your operational history includes specializing in the common narratives and recurring falsehoods that dominate disinformation 
        landscapes. You've built and constantly refine a compact yet potent internal database of frequently contested claims, scientific consensuses, and widely debunked myths. Your methodology prioritizes immediate verification against 
        these known data points, acting as a critical first line of defense against straightforward factual inaccuracies. While not exhaustive, your expertise lies in efficiently confirming or refuting claims that are often recycled in 
        misinformation campaigns, providing crucial initial signals for content validity.''',
        verbose = True, 
        tools=[search_tool],
        llm = llm 
    )

    # Defining Tasks
    # =============================================================================

    content_analysis_master_task = Task(

        description='''

            Thoroughly analyze the provided news article text {extracted_news_article_text}, leveraging a decade of experience in linguistic forensics to identify subtle and overt indicators often associated with misinformation. 
            This involves a multi-faceted assessment:

            1.  Sentiment Analysis: Determine the overarching emotional tone (positive, negative, neutral, mixed) and the intensity of the sentiment expressed throughout the article. 
                Look for disproportionate emotional loading that aims to provoke rather than inform.
            2.  Stylistic and Rhetorical Analysis: Identify specific writing styles that deviate from standard journalistic practice. This includes detecting:
                - Sensationalism: Use of hyperbole, exaggerated language, or dramatic framing to incite strong reactions.
                - Emotional Manipulation: Direct appeals to emotion (fear, anger, patriotism, pity) instead of logical arguments or evidence.
                - Overt Bias: Consistent use of loaded language, cherry-picking facts, or an unbalanced presentation of arguments that clearly favor one side or narrative.
                - Clickbait Elements: Headlines or phrasing designed solely to attract clicks, often sacrificing factual integrity, nuance, or contextual accuracy.
            3.  Linguistic Quality Assessment:** Scrutinize the text for grammatical inconsistencies, syntactical errors, frequent typos, or awkward phrasing that suggests a lack of professional editorial oversight. 
                These linguistic flaws can be a subtle indicator of less credible sources or rushed, unchecked content.
            4.  Factual Claim Extraction:** Precisely identify and extract between 3 to 5 distinct, verifiable factual claims made within the article. These claims should be concise statements amenable to 
                external verification (e.g., specific dates, names, events, statistics, or direct assertions).

            The ultimate aim is to provide a granular textual fingerprint of the article, highlighting linguistic patterns that strongly correlate with either authentic reporting or deceptive content.''',
            
        expected_output='''

        A structured JSON object containing: 
            - 'sentiment': { 'overall_tone': 'positive'|'negative'|'neutral'|'mixed', 'intensity': 'low'|'medium'|'high' }
            - 'sensationalism_level': 'low'|'medium'|'high'
            - 'bias_indicators': { 'identified_bias_phrases': ['phrase1', 'phrase2'], 'overall_strong_bias': true|false }
            - 'grammar_issues_detected': true|false
            - 'extracted_claims': ['claim1_text', 'claim2_text', 'claim3_text']
            - 'linguistic_flaws': { 'typos': true|false, 'awkward_phrasing': true|false, 'editorial_oversight': true|false }
            - 'clickbait_elements': { 'identified_clickbait_phrases': ['phrase1', 'phrase2'], 'overall_clickbait': true|false }
        ''',
        agent=content_analysis_master,
        async_execution= True
    )

    source_credibility_expert_task = Task(

        description='''
            Meticulously assess the trustworthiness and historical reliability of the news source (domain) from which the article originated. 
            Leveraging over 12 years of specialized experience in media forensics and dynamic online information evaluation, this involves:

                1.  Domain Extraction: Accurately parse the article's URL to extract the base domain name.
                2.  Strategic Web Search: Utilizing the SerperDev Tool, craft and execute targeted Google search queries for the extracted domain. Queries will aim to uncover reputation, 
                    potential biases, and historical accuracy, e.g., "[domain name] credibility," "[domain name] bias," "fact check [domain name] reviews," "who owns [domain name]".
                3.  Search Result Analysis: Systematically evaluate the top search results returned by the SerperDev Tool. This involves:
                    - Identifying mentions by established media watchdog organizations, fact-checking websites (e.g., Snopes, PolitiFact, Media Bias/Fact Check), or reputable journalistic ethics bodies.
                    - Looking for common public perception or critical analyses regarding the source's reporting consistency, accuracy, or known editorial stances.
                    - Reviewing "About Us" pages or Wikipedia entries linked in search results for transparency, mission statements, and ownership information.
                    - Detecting widespread criticisms or repeated accusations of misinformation, propaganda, or partisan agenda.

            The objective is to synthesize these real-time search findings into a swift yet authoritative judgment on the source's standing, which serves as a foundational input 
            for evaluating the article's overall veracity.''',

        expected_output='''
           A structured JSON object containing: 
            - 'source_url': (The original URL of the article)
            - 'domain': (The extracted base domain, e.g., 'example.com')
            - 'credibility_rating': 'high'|'medium'|'low'|'fake'|'unknown'
            - 'reasoning_summary': (A concise string summarizing the key findings from the web search that led to the rating, 
               e.g., 'Google search indicates frequent criticism for partisan bias on [domain].com', 
                     'Multiple top results from fact-checking sites rate [domain].com as unreliable', 
                     'Search results consistently show [domain].com as a reputable news organization', 
                     'Insufficient verifiable information found for [domain].com in search results')
        ''',
        agent=source_credibility_expert,
        tools=[search_tool],
        async_execution=True
    )

    claim_verification_specialist_task = Task(

        description='''
            As the Claim Verification Specialist, your primary task is to receive a precise list of factual claims extracted by the Content Analysis Master 
            and perform real-time verification using dynamic web searches. 
            Leveraging 8 years of focused experience in advanced information retrieval and dynamic information validation, this involves:

            1.  Claim Ingestion: Accept the list of distinct factual claims directly provided by the Content Analysis Master.
            2.  Strategic Web Search Execution: For each received claim, utilize the SerperDev Tool to craft and execute highly specific Google search queries designed to ascertain its veracity. 
                Queries will be formulated to directly target factual confirmation or refutation, e.g., "is [claim text] true," "[claim text] debunked," "[claim text] fact check."
            3.  Search Result Analysis and Synthesis: Systematically evaluate the top search results returned by the SerperDev Tool for each claim. This meticulous analysis includes:
                 - Identifying direct answers or strong consensus among highly authoritative and reputable sources (e.g., academic institutions, government bodies, established news organizations known for accuracy).
                 - Detecting explicit debunking by recognized fact-checking websites (e.g., Snopes, PolitiFact, FactCheck.org).
                 - Assessing the presence of significant counter-evidence or conflicting information from credible sources.
                 - Determining the recency and relevance of the information presented in search snippets.
            4.  Status Assignment: Based on the synthesis of web search findings, assign a precise verification status to each claim:
                 - 'verified': If multiple authoritative sources directly confirm the claim.
                 - 'debunked': If multiple authoritative sources or recognized fact-checkers explicitly refute or debunk the claim.
                 - 'unverifiable': If the web search yields insufficient direct evidence, conflicting information from credible sources, or no clear consensus to definitively confirm or refute the claim.

            Your objective is to provide a swift and accurate initial assessment of the claims' veracity by cross-referencing them with external authoritative data, acting as a crucial filter against widespread factual inaccuracies.''',
        
        expected_output='''
        
        A structured JSON object containing a list of dictionaries, where each dictionary represents a claim and its verification status: 
        [   
          {  'claim_text': 'Claim 1 text',     
             'verification_status': 'verified'|'debunked'|'unverifiable', 
             'reasoning_note': 'Matched a known verified fact in internal database'|'Matched a known debunked myth in internal database'|'No direct match found in internal database'
          }, 
          { 'claim_text': 'Claim 2 text', 
            'verification_status': 'verified'|'debunked'|'unverifiable', 
            'reasoning_note': 'Matched a known verified fact in internal database'|'Matched a known debunked myth in internal database'|'No direct match found in internal database' 
          }
        ]''',
        tools=[search_tool],
        agent=claim_verification_specialist
    )

    # Creating Crew
    # =============================================================================


    crew = Crew(
        agents=[content_analysis_master, source_credibility_expert, claim_verification_specialist],
        tasks=[content_analysis_master_task, source_credibility_expert_task, claim_verification_specialist_task],
        llm=llm,
        verbose=True
    )

    # Running the Scrape Website Tool to extract news article text and passing it to the Crew 
    extracted_news_article_text = scrape_website_tool.run()

    inputs = {
        "extracted_news_article_text" : extracted_news_article_text
    }

    # Running the Crew
    result = crew.kickoff(inputs=inputs)

    print(result)