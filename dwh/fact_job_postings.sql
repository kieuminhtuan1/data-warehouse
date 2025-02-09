CREATE TABLE fact_job_postings (
    job_id VARCHAR(50) PRIMARY KEY,
    url_job TEXT,
    job_title TEXT,
    company_id VARCHAR(50) REFERENCES dim_company(company_id),
    industry_id VARCHAR(50) REFERENCES dim_industry(industry_id),
    working_location_id VARCHAR(50) REFERENCES dim_working_location(working_location_id),
    working_time_id VARCHAR(50) REFERENCES dim_working_time(working_time_id),
    job_type_id VARCHAR(50) REFERENCES dim_job_type(job_type_id),
    salary VARCHAR(255),
    number_candidate INT,
    year_of_experience INT,
    due_date DATE
);
