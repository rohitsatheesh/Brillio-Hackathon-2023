# Brillio-Hackathon-2023

# GenAI HR App

The GenAI HR App is a streamlined application developed using Streamlit, BERT (Bidirectional Encoder Representations from Transformers), and MongoDB Atlas to efficiently match job candidates with job openings, enabling HR professionals to manage candidate selection, automate communication, and facilitate the hiring process.

## Features

- **Resume Information Extraction:** Utilizes OpenAI API to extract relevant information from candidate resumes.
- **BERT Matching Algorithm:** Employs BERT for accurate candidate-job matching based on skillsets, qualifications, and job requirements.
- **MongoDB Atlas Integration:** Stores and manages candidate and job data using MongoDB Atlas, ensuring secure and scalable database operations.
- **Candidate Shortlisting:** Enables HR personnel to efficiently shortlist candidates based on the matching algorithm results.
- **Automated Email Communication:** Facilitates the automation of sending emails to candidates, containing interview details such as link, date, and time.
- **Job Management:** Provides the capability for HR to add and manage job openings within the system.

## Installation

To run the GenAI HR App locally, follow these steps:

1. Clone this repository: `git clone <repository_url>`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up necessary API keys:
   - OpenAI API key: Obtain your API key from OpenAI and set it up in the configuration file.
   - MongoDB Atlas: Configure the database connection by providing the necessary credentials.

## Usage

1. Start the application by running: `streamlit run app.py`.
2. Access the app interface through the provided URL (typically http://localhost:8501).
3. Use the intuitive user interface to:
   - Upload candidate resumes for information extraction.
   - Add job openings to the system.
   - Match candidates to available jobs.
   - Shortlist candidates based on matches.
   - Automate email communication with interview details.
   - Manage job listings.

## Dependencies

Key libraries and tools used in this project:

- Streamlit
- TensorFlow (for BERT)
- OpenAI API
- MongoDB Atlas (pymongo)
