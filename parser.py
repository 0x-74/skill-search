import os
import time
from typing import Literal, Union

import pandas as pd
import dspy
from dotenv import load_dotenv

# ------------------------------------------------------------------
# LLM CONFIG
# ------------------------------------------------------------------
load_dotenv()
# lm = dspy.LM("groq/llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
lm = dspy.LM(
    "ollama_chat/gemma3:27b-it-qat",
    api_base="http://localhost:11434",
    api_key="",

)
dspy.configure(lm=lm)


# ------------------------------------------------------------------
# SIGNATURE
# ------------------------------------------------------------------
class JobDetails(dspy.Signature):
    """Extract detailed job information from a listing."""
    job_text: str = dspy.InputField()

    company: str = dspy.OutputField(desc="Name of the company")
    job_title: str = dspy.OutputField(
        desc="standardized format: seniority (junior, senior), title (full-stack, web, ml), role (engineer, intern)"
    )
    location: str = dspy.OutputField(desc="Job location")
    domain: str = dspy.OutputField(desc="Domain of work: AI, web, development, full-stack")
    domain_specific_skills: str = dspy.OutputField(
        desc="Technical skills relevant to the domain (e.g., opencv, pandas, numpy, tensorflow)"
    )
    work_model: str = dspy.OutputField(desc="Work model (e.g., Hybrid, Full-time)")
    min_experience: int = dspy.OutputField(desc="Minimum experience in years")
    max_experience: int = dspy.OutputField(desc="Maximum experience in years")
    number_of_employeees: str = dspy.OutputField(desc="Number of employees in the company")  # NOTE: field name kept as-is
    weeks_since_posting: int = dspy.OutputField(desc="Weeks passed since posting date")
    min_salary: Union[None, int] = dspy.OutputField(desc="Minimum pay range")
    max_salary: Union[None, int] = dspy.OutputField(desc="Maximum pay range")
    no_of_applicants: int = dspy.OutputField(desc="Number of people that clicked apply")
    company_type: str = dspy.OutputField(desc="Type, size, funding stage")
    key_responsibilities: str = dspy.OutputField(desc="Key responsibilities / tasks")
    technical_requirements: str = dspy.OutputField(desc="Required technical skills / technologies")
    education: Literal["Bachelors", "Masters", "Phd"] = dspy.OutputField(desc="Minimum required educational background")
    benefits_culture: str = dspy.OutputField(desc="Company culture, benefits, perks")
    unique_aspects: str = dspy.OutputField(desc="Unique aspects of the role or company")
    application_link: Union[None, str] = dspy.OutputField(desc="How to apply / URL")  # changed to str; was int
    applicant_insights: str = dspy.OutputField(desc="Insights on typical applicants / experience levels")


# Instantiate the parser *after* defining the signature.
job_parser = dspy.ChainOfThought(JobDetails)


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def parse_single_job(job_text: str):
    """Return dict for one job block; None on failure."""
    try:
        result = job_parser(job_text=job_text)
        return result.toDict()
    except Exception as e:
        print(f"failed to parse job: {e}")
        return None


def parse_jobs_file(path: str, separator: str = "-" * 80, sleep_s: int = 60) -> pd.DataFrame:
    """Parse all jobs in a flat text file separated by a repeated hyphen line."""
    with open(path, "r", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split(separator) if c.strip()]

    rows = []
    for idx, chunk in enumerate(chunks):
        job_dict = parse_single_job(chunk)
        if job_dict is None:
            print(f"skipping index {idx}")
            continue
        rows.append(job_dict)
        if sleep_s:
            time.sleep(sleep_s)

    return pd.DataFrame(rows)