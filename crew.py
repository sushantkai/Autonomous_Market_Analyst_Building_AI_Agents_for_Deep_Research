import os

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI


def build_crew(topic: str, google_api_key: str, serper_api_key: str) -> Crew:
    os.environ["SERPER_API_KEY"] = serper_api_key

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=google_api_key,
    )

    search_tool = SerperDevTool()

    researcher = Agent(
        role="Market Researcher",
        goal=f"Find and analyze the latest trends related to: {topic}",
        backstory=(
            "You are an expert market researcher skilled at finding relevant information "
            "and synthesizing it into clear summaries."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=gemini_llm,
    )

    writer = Agent(
        role="Content Writer",
        goal=f"Write a compelling blog post about: {topic}",
        backstory=(
            "You are a renowned content writer who turns complex topics into engaging articles "
            "for a wide audience."
        ),
        verbose=True,
        allow_delegation=True,
        llm=gemini_llm,
    )

    research_task = Task(
        description=(
            f"Research the latest trends related to: {topic}. Focus on significant advancements, "
            "emerging technologies, and key players. Produce a detailed report."
        ),
        expected_output="A comprehensive report summarizing the latest trends.",
        agent=researcher,
    )

    write_task = Task(
        description=(
            "Write a blog post based on the research findings. Make it engaging, informative, "
            "and accessible to a non-technical audience."
        ),
        expected_output="A 500-word blog post on the researched topic.",
        agent=writer,
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


def run_market_analysis(topic: str, google_api_key: str, serper_api_key: str) -> str:
    crew = build_crew(topic, google_api_key, serper_api_key)
    result = crew.kickoff()
    return getattr(result, "raw", result)
