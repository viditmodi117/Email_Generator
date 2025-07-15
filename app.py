from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

# Set your Groq API key here
os.environ['GROQ_API_KEY'] = ' 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'

# Initialize the Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-email', methods=['POST'])
def generate_email():
    data = request.get_json()

    # Extract user data from the form
    name = data.get('name')
    user_email = data.get('email')
    contact_number = data.get('contactNumber')
    linkedin_profile = data.get('linkedinProfile')
    github_profile = data.get('githubProfile', 'N/A')
    previous_experience = data.get('previousExperience', 'N/A')
    skills = data.get('skills')
    interest_reason = data.get('interestReason')
    job_description = data.get('jobDescription')
    company_name = data.get('companyName')
    company_email = data.get('companyEmail')

    # LLM prompt to generate the job application email
    prompt = f"""
    Write a professional job application email for the following job description: {job_description}.
    The applicant's details are:
    Full Name: {name}
    Previous Experience: {previous_experience}
    Skills: {skills}
    Interested in {company_name} because: {interest_reason}

    The email should include:
    1. Subject line: Be specific about the position and company name.
    2. Introduction: Briefly introduce yourself and state your intention.
    3. Skills and experience: Highlight relevant skills and match them with job responsibilities.
    4. Interest in the company: Show genuine interest in the role and the company.
    5. Resume attachment information: Mention that the resume is attached.
    """

    # Generate the email using the Groq client and llama3-groq-70b-8192-tool-use-preview model
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.83,
        max_tokens=1200,
        top_p=0.65,
        stream=True,
        stop=None,
    )

    # Collect generated email from the model's stream
    generated_email = ""
    for chunk in completion:
        generated_email += chunk.choices[0].delta.content or ""

    # Remove extra space before name in the closing
    generated_email = generated_email.replace("Best regards,\n\n", "Best regards,\n")

    # Format contact information with clickable links
    contact_info = (
        f"\n\nEmail: <a href='mailto:{user_email}'>{user_email}</a>\n"
        f"Phone: <a href='tel:{contact_number}'>{contact_number}</a>\n"
        f"LinkedIn: <a href='{linkedin_profile}' target='_blank'>{linkedin_profile}</a>\n"
        f"GitHub: <a href='{github_profile}' target='_blank'>{github_profile}</a>"
    )

    # Return the generated email as JSON
    return jsonify({"email": generated_email + contact_info})

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()

    # Simulate sending the email
    company_name = data.get('companyName')
    
    # Return a success message after "sending" the email
    return jsonify({"message": f"Email successfully sent to {company_name}!"})

if __name__ == '__main__':
    app.run(debug=True)
