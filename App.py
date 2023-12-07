from PyPDF2 import PdfReader
import streamlit as st
st.set_option('deprecation.showfileUploaderEncoding', False)
st.production = True
from docx2pdf import convert 
import openai
import io
import base64
from datetime import datetime,  timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from transformers import BertTokenizer, BertModel
import torch
from PyPDF2 import PdfReader 
from pymongo import MongoClient
import json


# Replace the following connection string with your MongoDB URI
mongo_uri = "mongodb+srv://admin:admin@cluster0.94180nh.mongodb.net/"

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["your_database"]  
collection = db["resumes"] 
Jobs_Available=db["jobs"]

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

#openai api key
openai.api_key="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"

def flatten_list(lst):
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened

#the prompt to extract necessary information from resume
def resume_to_json(resume, years_of_experience):
    instructPrompt = """"
    You're part of system trying to classify resume.
    I will send you the OCR output of a resume. 
    You should answer a JSON document with the following : 
    - Full name 
    - Study 
    - Experiences 
    - Years of experience (in years and decimals)
    - Skills . 
    Be careful, the OCR being not perfect, some line might be written in a weird way or may be cut off. 
    Start by reassambling the text, and answer only a JSON.
    Here is the OCR output ;
    """
    # flattened_resume = flatten_list(resume)
    resume = [str(item) for item in resume]
    resume= " ".join(resume)
    # resume= " ".join(str(item) for item in flattened_resume)
    request=instructPrompt + resume  + f"\nYears of experience: {years_of_experience}"
    chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                      {"role": "user", "content": request}
                                                      ]
                                            )
    return chatOutput.choices[0].message.content

def split_text_to_fit_token_limit(text, max_token_length=512):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Tokenize the text
    tokens = tokenizer.tokenize(text)

    # Check if the number of tokens exceeds the maximum limit
    if len(tokens) > max_token_length:
        # Split the text into smaller chunks that fit within the token limit
        # token_chunks = [tokens[i:i + max_token_length] for i in range(0, len(tokens), max_token_length)]
        tokens = tokens[:max_token_length]
        # return token_chunks
        return tokens
    else:
        # If the text length is within the limit, return the original text as a single chunk
        return [tokens]

#extracting text from pdf
def extract_text_with_pdfreader(uploaded_file):
    pdf_reader = PdfReader(io.BytesIO(uploaded_file))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    token_chunks = split_text_to_fit_token_limit(text)

    return token_chunks



#page one to upload resumes and extract using OpenAI
def page_one():
    st.title("Applicant Page !")
    user_email = st.text_input("Enter your email")
    years_of_experience = st.number_input("Enter your years of experience", min_value=0.0, step=0.1)
    file_paths = st.file_uploader("Upload a PDF", type="pdf",accept_multiple_files=True)
    if file_paths:
        st.write("Processing...")
        for file_path in file_paths:
            file_data = file_path.read()
            if file_path.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                with io.BytesIO() as pdf_output:
                    convert(io.BytesIO(file_data), pdf_output)
                    file_data = pdf_output.getvalue()   

            resume = extract_text_with_pdfreader(file_data)
            
            json_data = resume_to_json(resume,years_of_experience)
            
            resume_record = {
                'user_email': user_email,  # Store user email along with the resume
                'File_name': file_path.name,
                'data': file_data ,# Store the file data as binary (PDF)
                'json_data': json.loads(json_data)# Store extracted text using OpenAI
            }
            collection.insert_one(resume_record)
            
                           
        st.success(f"{len(file_paths)} resumes uploaded successfully!")


def page_three():
    st.title("HR Made Simple !")
    st.title("Add Job Title and Description")
    job_title = st.text_input("Enter Job Title")
    job_description = st.text_area("Enter Job Description")

    if st.button("Add Job"):
        if job_title and job_description:
            job_record = {
                'job_title': job_title,
                'job_description': job_description
            }
            result_job = db['jobs'].insert_one(job_record)
            st.success("Job added successfully!")
        else:
            st.warning("Please enter both job title and description.")





def send_email(candidate_email,selected_job,interview_date,interview_time,url,emails):
    # Email configuration
    email_sender = 'rohitsatheesh@gmail.com'
    email_receiver = candidate_email
    subject = 'Invitation for Interview'
    # message = f"""Dear applicant,\n\nCongratulations!You've been shortlisted for the position of {selected_job} based on your skills and experience.Your interview details are:
    #             \n Date : {interview_date} and Time : {interview_time} 
    #             \nWe're excited to dsicuss your qualifications further.Prepare to delve into your skills and experience in relation to your role .
    #             \n Please confirm your availibilty by EOD.If needed ,let us know of any scheduling conflicts or accommodations required.
    #             \nLooking forward to meeting you,
    #             \nRegards,
    #             \nBriliio Talent Aquisition Team"""
    if emails > 0 :
        interview_time= datetime.combine(datetime.today(), interview_time) + timedelta(minutes=30)
    else :
        pass
    selected_time_12h = interview_time.strftime("%I:%M %p")
         
    message = f"""Dear applicant,
    

    Congratulations! You've been shortlisted for the position of {selected_job} based on your skills and experience. Your interview details are:

    Date: {interview_date}
    Time: {selected_time_12h}
    Link:{url}

    Please confirm your availability by EOD. If needed, let us know of any scheduling conflicts or accommodations required. We're excited to discuss your qualifications further. 
    Prepare to delve into your skills and experience in relation to your role.

    Looking forward to meeting you,

    Regards,
    Briliio Talent Acquisition Team"""


    # SMTP server configuration (for example, Gmail)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'rohitsatheesh@gmail.com'
    smtp_password = 'fnpq spcc mgim rgkj'
    try:
    # Create message container - the correct MIME type is multipart/alternative
        msg = MIMEMultipart('alternative')
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = subject

        # Attach message to email body
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send email
        server.sendmail(email_sender, email_receiver, msg.as_string())

        # Terminate the SMTP session and close connection
        server.quit()
        return (f"Email sent successfully to {email_receiver}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Failed to send email to {email_receiver}")



            
def match(selected_job, num_resumes, experience_range):
    job_query = Jobs_Available.find_one({'job_title': selected_job})
    
    job_description = job_query.get('job_description', '')
    candidate_emails=[]
    candidate_info = []
    candidate_names = []
    
    similarity_scores = []
    found_candidates = False  # Flag to track if any candidates were found

    for resume_info in collection.find():
        candidate_experience = resume_info['json_data'].get('Years of experience', 0)  # Assuming this field exists
        if experience_range[0] <= candidate_experience <= experience_range[1]:
            found_candidates = True
            full_name = resume_info['json_data'].get('Full name', 'N/A')
            if full_name:
                capitalized_name = ' '.join(word.capitalize() for word in full_name.split())
            else:
                capitalized_name = 'N/A'
            # capitalized_name = ' '.join(word.capitalize() for word in full_name.split())  # Capitalize each word
            candidate_names.append(capitalized_name)
            candidate_email = resume_info.get('user_email', 'N/A')
            resume_data = resume_info['data']  # Resume data for download
            skills = resume_info['json_data'].get('Skills', '')
            experience = resume_info['json_data'].get('Experiences', '')
            study = resume_info['json_data'].get('Study', '')

            combined_text = f"{skills} {experience} {study}"

            encoded_job = tokenizer.encode(job_description, add_special_tokens=True, return_tensors='pt')
            with torch.no_grad():
                job_embedding = model(encoded_job)[0][:, 0, :].squeeze()

            encoded_candidate = tokenizer.encode(combined_text, add_special_tokens=True, return_tensors='pt')
            with torch.no_grad():
                candidate_embedding = model(encoded_candidate)[0][:, 0, :].squeeze()

            similarity = torch.cosine_similarity(job_embedding, candidate_embedding, dim=0).item()
            similarity_scores.append(similarity)
            candidate_info.append((capitalized_name, candidate_email, similarity,resume_data))  # Add name, email, similarity
            
    
    sorted_candidates = sorted(candidate_info, key=lambda x: x[2], reverse=True)[:num_resumes]
    table_data = {'Candidate Name': [candidate[0] for candidate in sorted_candidates],
                          'Email': [candidate[1] for candidate in sorted_candidates],
                          'Similarity Score': [candidate[2] for candidate in sorted_candidates]}
    st.subheader(f"Matching Candidates")
    st.table(table_data)
    
    candidate_emails.append([candidate[1] for candidate in sorted_candidates])

      
    return candidate_emails

    
   
    


def page_two():
    st.title("HR Made Simple !")
    available_jobs = [job['job_title'] for job in Jobs_Available.find()]
    selected_job = st.selectbox("Select a Job Title", available_jobs)

    # Create a slider to retrieve the number of resumes
    num_resumes = st.slider("Select number of resumes", min_value=1, max_value=100, value=10)

    # Create a sidebar slider for filtering candidates based on experience
    experience_range = st.slider('Experience (years)', 0, 20, (0, 10))
    
    form = st.form(key='my_form')
    form2=st.form(key='my_form_2')
    abc = match(selected_job, num_resumes, experience_range)
    options = [email for sublist in abc for email in sublist] if abc is not None else [None]

    selected_email = form.selectbox("Select Resume ", [None] + options)
    
    submitted = form.form_submit_button('View Resume')

    if submitted and selected_email is not None:
        placeholder = st.empty()
        resume_data = collection.find_one({'user_email': selected_email})
        if resume_data:
            pdf_data = resume_data['data']
            
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf">'
            placeholder.markdown(pdf_display, unsafe_allow_html=True)

    # default_time = None
    selected_emails_2 = form2.multiselect("Select Emails ", options)
    interview_date = form2.date_input("Select Interview Date", min_value=None, max_value=None)
    interview_time = form2.time_input("Select a time")
    url = form2.text_input("Interview URL")
    submitted_emails = form2.form_submit_button('Send Email')
    emails=0
    if submitted_emails and selected_emails_2 and interview_date and interview_time:
        for email in selected_emails_2:
            result = send_email(email, selected_job, interview_date, interview_time, url,emails)
            emails += 1
            st.write(result if result else f"Email sent to {email}")




def display_pdf_4(pdf_data, file_name):
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

def render_resume_4(selected_email):
   
    if selected_email:
        resume_data = collection.find_one({'user_email': selected_email})
        if resume_data:
            display_pdf_4(resume_data['data'], resume_data['File_name'])

        else:
            st.write("Resume not found for the selected email.")


def page_four():
    st.title("View Resumes")
    all_emails = [record['user_email'] for record in collection.find({}, {'user_email': 1})]
    selected_email = st.selectbox("Select Email to View Resumes", [None]+all_emails)
    if selected_email is not None:
        render_resume_4(selected_email)

   

def main():
    
    st.sidebar.title("Welcome!")
    page_options = ["Upload Resumes", "Dashboard","Add Job", "View Resumes"]
    selected_page = st.sidebar.selectbox("Go to", page_options)

    if selected_page == "Upload Resumes":
        page_one()
    elif selected_page == "Dashboard":
        page_two()    
    elif selected_page == "Add Job":
        page_three()
    elif selected_page == "View Resumes":
        page_four()
    
        
              
if __name__ == '__main__':
    main()


