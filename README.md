# Stage 2
## pandas-ai based chatbot to query jobs data for Delhi and Gurgaon

### Description
This stage develops a chatbot using `pandas-ai` that allows users to query job data specifically for Delhi and Gurgaon. The chatbot helps users explore and analyze job listings across various sectors, companies, and roles available in these two major cities.

### Features
- **Natural Language Querying**: Users can ask questions in everyday language, and the chatbot interprets these queries into pandas DataFrame operations.
- **Job-Specific Queries**: The chatbot focuses on job data in Delhi and Gurgaon, enabling users to:
  - Find specific jobs by title, sector, or company
  - Filter jobs based on salary ranges, experience, and job type (full-time, part-time, remote, etc.)
  - Analyze job trends, such as the most common job titles, sectors with the most openings, or top hiring companies
- **Context-Aware**: The chatbot understands that queries should only relate to jobs in Delhi and Gurgaon.

### Example Queries
- *"List all software engineering jobs in Delhi with a salary above 10 LPA."*
- *"Show the top 5 companies hiring in Gurgaon for data analysts."*
- *"Find remote jobs in Delhi for freshers in the marketing field."*
- *"What are the average salaries for backend developers in Gurgaon?"*

### Next Steps
- **Improve Query Understanding**: Handle more complex multi-condition queries like filtering by multiple job attributes.
- **Add Visualization Support**: Allow the chatbot to display charts (e.g., pie charts for sector distribution, bar graphs for salary ranges).
- **Expand Dataset**: Incorporate additional data sources, such as company reviews and employee ratings.

