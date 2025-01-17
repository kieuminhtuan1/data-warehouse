from airflow import DAG
from airflow.operators.python import PythonOperator
import os
from datetime import datetime, timedelta
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pymysql
import csv
import json
import time
import random

BASE_URL = 'https://www.topcv.vn/tim-viec-lam-moi-nhat?sort=new&page='
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.topcv.vn/viec-lam',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
START_PAGE = 1
END_PAGE = 50
URLS_FILE = 'extracted_urls.txt'
HTML_FILE = 'urls_and_html.json'
CSV_FILE = "/opt/airflow/data/extracted_jobs_1-50.csv"

# Create a scraper instance
scraper = cloudscraper.create_scraper(browser='chrome')


def scrape_urls(**kwargs):
    """Scrape job URLs from TopCV."""
    try:
        with open(URLS_FILE, 'w') as file:
            for i in range(START_PAGE, END_PAGE + 1):
                url = f'{BASE_URL}{i}'
                time.sleep(random.uniform(2, 5))
                response = scraper.get(url, headers=HEADERS)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_links = soup.select('.title a')

                    for link in title_links:
                        href = link.get('href')
                        if href:
                            file.write(href + '\n')
                            print(href)
                else:
                    print(
                        f"Failed to retrieve page {i}. Status code: {response.status_code}")

        print(f"URLs successfully saved to {URLS_FILE}")
    except Exception as e:
        print(f"An error occurred while scraping URLs: {str(e)}")


def get_html_with_retry(url, retries=3):
    for attempt in range(retries):
        response = scraper.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 30))
            print(
                f"Rate limit reached for {url}. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            print(
                f"Failed to retrieve {url}. Status code: {response.status_code}")
            return None
    print(f"Max retries exceeded for {url}. Skipping.")
    return None


def download_html(**kwargs):
    """Download HTML content for each job URL."""
    try:
        with open(URLS_FILE, 'r') as file:
            urls = file.readlines()

        for url in urls:
            url = url.strip()
            if url:
                time.sleep(random.uniform(5, 15))
                html_content = get_html_with_retry(url)
                if html_content:
                    data = {'url': url, 'html': html_content}
                    with open(HTML_FILE, 'a', encoding='utf-8') as json_file:
                        json_file.write(json.dumps(
                            data, ensure_ascii=False) + '\n')
                    print(f"Successfully retrieved and saved HTML for: {url}")
    except Exception as e:
        print(f"An error occurred while downloading HTML: {str(e)}")


def extract_job_features(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract job title
    job_title = soup.find(class_='job-detail__info--title')
    job_title = job_title.text.strip() if job_title else None

    # Initialize variables
    salary = None
    year_of_experience = None
    job_city = None

    # Extract job details from sections
    sections = soup.find_all("div", class_="job-detail__info--section")
    for section in sections:
        section_title = section.find(
            "div", class_="job-detail__info--section-content-title")
        if section_title:
            title_text = section_title.text.strip()
            content_value = section.find(
                "div", class_="job-detail__info--section-content-value")
            content_value = content_value.text.strip() if content_value else None

            if title_text == "Mức lương":
                salary = content_value
            elif title_text == "Kinh nghiệm":
                year_of_experience = content_value
            elif title_text == "Địa điểm":
                job_city = content_value

    # Extract due date
    due_date = soup.find(class_='job-detail__info--deadline')
    due_date = due_date.text.strip() if due_date else None

    # Extract job description
    job_description = []
    items = soup.find_all('div', class_='job-description__item')
    for item in items:
        title = item.find('h3').get_text(
            strip=True) if item.find('h3') else None
        content = item.find('div', class_='job-description__item--content')
        content = content.get_text(strip=True) if content else None
        if title and content:
            job_description.append({'title': title, 'content': content})

    # Extract company details
    company_name = soup.select_one('.company-name .name')
    company_name = company_name.get_text(strip=True) if company_name else None

    company_scale = soup.select_one('.company-scale .company-value')
    company_scale = company_scale.get_text(
        strip=True) if company_scale else None

    company_field = soup.select_one('.company-field .company-value')
    company_field = company_field.get_text(
        strip=True) if company_field else None

    company_address = soup.select_one('.company-address .company-value')
    company_address = company_address.get_text(
        strip=True) if company_address else None

    # Return a dictionary with all the extracted information
    return {
        'job_title': job_title,
        'company_name': company_name,
        'company_scale': company_scale,
        'company_field': company_field,
        'company_address': company_address,
        'salary': salary,
        'year_of_experience': year_of_experience,
        'job_city': job_city,
        'due_date': due_date,
        'job_description': job_description
    }


def extract_job_data(**kwargs):
    """Extract job data and save to CSV."""
    extracted_data = []
    try:
        # Đọc dữ liệu từ HTML file
        with open(HTML_FILE, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    entry = json.loads(line)
                    url = entry.get('url')
                    html_content = entry.get('html')
                    job_features = extract_job_features(html_content)
                    job_features['url'] = url
                    extracted_data.append(job_features)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"Error extracting job features: {e}")

        if not extracted_data:
            print("No job data extracted.")
            return

        # Lưu dữ liệu ra file CSV
        try:
            with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as csv_file:
                writer = csv.DictWriter(
                    csv_file, fieldnames=extracted_data[0].keys())
                writer.writeheader()
                writer.writerows(extracted_data)
                print(f"Job data saved to {CSV_FILE} successfully.")
        except IOError as e:
            print(f"Error writing to CSV file: {e}")

    except FileNotFoundError:
        print("HTML file not found. Please check the file path.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'topcv_scraper',
    default_args=default_args,
    description='Scrape job postings from TopCV',
    schedule_interval='@once',
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    scrape_urls_task = PythonOperator(
        task_id='scrape_urls',
        python_callable=scrape_urls,
    )

    download_html_task = PythonOperator(
        task_id='download_html',
        python_callable=download_html,
    )

    extract_job_data_task = PythonOperator(
        task_id='extract_job_data',
        python_callable=extract_job_data,
    )

    scrape_urls_task >> download_html_task >> extract_job_data_task
