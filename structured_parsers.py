import dspy
import os
from dotenv import load_dotenv
from typing import Literal, Union
import pandas as pd
import time

# Load environment variables
load_dotenv()

# Initialize the language model
lm = dspy.LM('ollama_chat/gemma:27b-it-qat', api_base='http://localhost:11434', api_key='')
dspy.configure(lm=lm)
dspy.context(experimental=True)

# Define the schema for job details extraction
class JobDetails(dspy.Signature):
    """Extract detailed job information from a listing."""
    job_text: str = dspy.InputField()
    company: str = dspy.OutputField(desc="Name of the company")
    job_title: str = dspy.OutputField(desc="standardized job format in the sequence seniority(eg junior,senior), title(eg full-stack,web,ml), role (engineer,intern)")
    location: str = dspy.OutputField(desc="Job location")
    domain: str = dspy.OutputField(desc="Domain of work AI web,development,full-stack")
    domain_specific_skills: str = dspy.OutputField(desc="Technical skills only relevant to the current domain eg opencv,pandas,numpy,tensorflow for AI")
    work_model: str = dspy.OutputField(desc="Work model (e.g., Hybrid, Full-time)")
    min_experience: int = dspy.OutputField(desc="minimum experience level in years")
    max_experience: int = dspy.OutputField(desc="maximum experience level in years")
    number_of_employeees: str = dspy.OutputField(desc='number of employees working in company')
    weeks_since_posting: int = dspy.OutputField(desc="weeks passed since posting date")
    min_salary: Union[None, int] = dspy.OutputField(desc="minimum pay range")
    max_salary: Union[None, int] = dspy.OutputField(desc="maximum pay range")
    no_of_applicants: int = dspy.OutputField(desc="number of people that have clicked apply")
    company_type: str = dspy.OutputField(desc="Type of company, size, and funding stage")
    key_responsibilities: str = dspy.OutputField(desc="Key responsibilities and tasks for the role")
    technical_requirements: str = dspy.OutputField(desc="Required technical skills and technologies")
    education: Literal['Bachelors', 'Masters', 'Phd'] = dspy.OutputField(desc="minimum Required educational background")
    benefits_culture: str = dspy.OutputField(desc="Company culture, benefits, and perks")
    unique_aspects: str = dspy.OutputField(desc="Unique aspects of the role or company")
    application_link: Union[None, int] = dspy.OutputField(desc="How to apply for the job")
    applicant_insights: str = dspy.OutputField(desc="Insights on typical applicants and experience levels")

# Create the parser chain
job_parser = dspy.ChainOfThought(JobDetails)

# Read the jobs data
with open('jobs.txt', 'r', encoding='utf-8') as file:
    jobs = file.read().split('-' * 80)

# This flag tracks if the CSV header has been written
csv_file = 'structured_jobs_data.csv'
header_written = False

for idx, job_data in enumerate(jobs):
    try:
        data = job_parser(job_text=job_data)
        row_df = pd.DataFrame([data.toDict()])

        # Append to CSV, write header only on first write
        row_df.to_csv(csv_file, mode='a', index=False, header=not header_written)
        header_written = True

    except Exception as e:
        print(f'Failed to parse index {idx}: {e}, skipping...')
        with open('failed_jobs.txt', 'a', encoding='utf-8') as f_fail:
            f_fail.write(f'Index: {idx}\n')
            f_fail.write(job_data.strip())
            f_fail.write('\n' + '=' * 80 + '\n')
        continue

    time.sleep(60)
