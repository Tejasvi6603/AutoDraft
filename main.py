from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import json
from jinja2 import Template
import base64
import pandas as pd

def extract_info():
    print("Starting extract_info()...")
    
    options = Options()
    options.headless = False  # Set to True if you want the browser to run in the background

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=options)

    # Open the target website
    print("Opening website...")
    driver.get('https://www.datadoghq.com/technical-enablement/sessions/?tem_language-0=english')

    # Wait for the page to load
    time.sleep(5)

    # Find card elements
    print("Finding card elements...")
    cards = driver.find_elements(By.CSS_SELECTOR, 'li.ais-InfiniteHits-item')

    # Initialize an empty list for session data
    session_data = []

    # Loop through each card and extract relevant information
    for card in cards:
        try:
            register_link_element = card.find_element(By.CSS_SELECTOR, 'a.tw-block.tw-h-full.tw-w-full')
            register_link = register_link_element.get_attribute('href')

            title = card.find_element(By.CSS_SELECTOR, 'h3').text
            description = card.find_element(By.CSS_SELECTOR, 'p').text

            tags = card.find_elements(By.CSS_SELECTOR, 'a div span')
            tag_list = [tag.text for tag in tags if tag.text and not tag.text.startswith('+')]
            

            session_data.append({
                'title': title,
                'description': description,
                'tags': tag_list,
                'registerLink': register_link
                 
            })
            print(f"Extracted session: {title}")
        except Exception as e:
            print(f"Error extracting data from card: {e}")

    # Save session data as JSON
    with open('sessions.json', 'w') as json_file:
        json.dump(session_data, json_file)
    print("Session data saved to sessions.json")

    # Read the HTML template
    html_template_path = 'index_template.html'  # Path to your existing HTML template
    html_output_path = 'index.html'  # Path to save the updated HTML file

    print("Reading HTML template...")
    with open(html_template_path, 'r') as file:
        html_content = file.read()

    # Prepare the session data for insertion
    session_cards_html = ''
    for session in session_data:
        tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in session['tags']])
        session_cards_html += f'''
        <div class="session-card">
            <h2 class="session-title">{session['title']}</h2>
            <p class="session-description">{session['description']}</p>
            <div class="session-tags">{tags_html}</div>
            <a href="{session['registerLink']}">Register</a>
        </div>'''

    # Insert the session data into the HTML content
    html_content = html_content.replace('<!-- INSERT_SESSION_CARDS -->', session_cards_html)

    # Save the updated HTML file
    with open(html_output_path, 'w') as file:
        file.write(html_content)
    print(f"HTML file updated and saved in: {os.path.abspath(html_output_path)}")
    
    driver.quit()
    print("Finished extract_info()")

def htmlcreate():
    print("Starting htmlcreate()...")
    
    filename = 'sessions.json'
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            session_data = json.load(json_file)
        print("Loaded session data from sessions.json")
    else:
        session_data = []
        print("No session data found.")

    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
            .navbar { background-color: #774aa4; padding: 10px; text-align: center; margin: -20px; height: 34px; }
            .navbar-item { color: white; margin: 0 15px; text-decoration: none; font-weight: bold; font-size: 21px; }
            .navbar-item:hover { text-decoration: underline; }
            .send-email-button { background-color: green; color: white; border: none; border-radius: 5px; padding: 10px; cursor: pointer; font-size: 0.9em; margin-top: -5px; float: right; }
            .sessions-container { display: flex; flex-wrap: wrap; justify-content: center; margin-top: 56px; }
            .session-card { background-color: #ffffff; border: 1px solid #e2e2e2; border-radius: 8px; padding: 15px; margin: 10px; width: 300px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); transition: transform 0.2s; cursor: pointer; }
            .session-card:hover { transform: scale(1.05); }
            .session-title { font-size: 1.5em; margin: 0; color: #101010; }
            .session-description { margin: 5px 0; color: #19191a; }
            .session-tags { margin-top: 10px; }
            .intro-cards-container {
            display: flex;
            justify-content: space-around;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        .intro-card {
            background-color: #c99bf6; /* Violet color */
            border: 1px solid #e2e2e2;
            border-radius: 8px;
            padding: 5rem;
            margin: 1.5rem;
            width: 28rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
            cursor: pointer;
            text-align: center;
            color: black;
        }
        .intro-card:hover {
            transform: scale(1.05); /* Hover effect */
            background-color: #b834ec; /* Darker violet on hover */
        }
        .intro-card h3 {
            font-size: 2.0em;
            margin-bottom: 10px;
        }
        .intro-card p {
            font-size: 1.3em;
        }
            .tag { background-color: #e0e7ff; border-radius: 5px; padding: 5px; margin-right: 5px; display: inline-block; font-size: 0.9em; color: #774aa4; margin-top: 10px; }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="#" class="navbar-item">Home</a>
            <a href="#" class="navbar-item">Sessions</a>
            <a href="https://www.datadoghq.com/about/leadership/" class="navbar-item">About</a>
            <a href="#" class="navbar-item">Contact</a>
            <button class="send-email-button" onclick="openEmlFile()">Send Email</button>
        </nav>

         <div class="intro-cards-container">
        <div class="intro-card">
            <h3>Foundation Enablement</h3>
            <p>Sessions available on this platform.</p>
        </div>
        <div class="intro-card">
            <h3>Training Sessions</h3>
            <p>Planned on a monthly basis.</p>
        </div>
        <div class="intro-card">
            <h3>View the Session Calendar</h3>
            <p>Check out the available sessions and plan ahead.</p>
        </div>
        <div class="intro-card">
            <h3>You Can Select:</h3>
            <p>Topics, Level, Language</p>
        </div>
    </div>

        <div class="sessions-container">
            {% for session in sessions %}
            <div class="session-card" onclick="window.location.href='{{ session.registerLink }}'">
                <h2 class="session-title">{{ session.title }}</h2>
                <p class="session-description">{{ session.description }}</p>
                <div class="session-tags">
                    {% for tag in session.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>

        <script>
            function openEmlFile() {
                window.location.href = 'File.eml';  // Update with the correct path to your .eml file
            }
        </script>
    </body>
    </html>
    """

    # Render the HTML template with session data
    print("Rendering HTML template...")
    template = Template(html_template)
    html_content = template.render(sessions=session_data)

    # Save the rendered HTML to a file
    output_html_file = 'index.html'
    with open(output_html_file, 'w') as file:
        file.write(html_content)
    
    print(f"HTML file generated: {os.path.abspath(output_html_file)}")
    print("Finished htmlcreate()")

def encode_file_to_base64(file_path):
    try:
        print(f"Encoding file to base64: {file_path}")
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def create_draft_email_with_attachment():
    # Prompt for the sender's email address
    sender = input("Enter the sender's email address: ")
    
    # Prompt for multiple recipients
    excel_file_path = "output.xlsx"  # Path to your Excel file
    try:
        df = pd.read_excel(excel_file_path)
        recipients_list = df["Email"].dropna().tolist()  # Assuming the column with email is named 'Email'
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return

    if not recipients_list:
        print("No recipients found in the Excel file.")
        return

    recipients_str = ", ".join(recipients_list)
    
    recipients_str = ", ".join(recipients_list)
    

    # Email subject and body
    subject = "Datadog Session"
    # plain_body = "This is a plain text version of the email."s
    html_body = """
   <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
        <style type="text/css">
            body {
                font-family: Aptos, Aptos_EmbeddedFont, Aptos_MSFontService, Calibri, Helvetica, sans-serif;
                font-size: 12pt;
                color: rgb(0, 0, 0);
                line-height: 1.5;
                margin: 20px;
                background-color: #f9f9f9; /* Light background */
            }
            .email-container {
                background-color: #ffffff; /* White background for the box */
                border: 2px solid black; /* Black border */
                border-radius: 0; /* No rounded corners */
                padding: 20px; /* Inner padding */
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */
                max-width: 600px; /* Maximum width */
                margin: auto; /* Center the box */
            }
            p {
                margin: 0 0 1em;
            }
            ol {
                margin-left: 20px;
                padding-left: 10px;
            }
            ul {
                margin-left: 20px;
                padding-left: 10px;
                list-style-type: disc;
            }
            a {
                color: #007BFF; /* Blue color for links */
                text-decoration: none; /* Remove underline */
            }
            a:hover {
                text-decoration: underline; /* Underline on hover */
            }
            strong {
                font-weight: bold;
            }
        </style>
    </head>
    <body dir="ltr">
        <div class="email-container">
            <p>Dear all,</p>
            <p>We have a Datadog online learning platform designed and accessible to all employees of IDeaS. The main purpose of this learning path is to broaden your knowledge of features within Datadog, familiarize yourself with core concepts, and learn best practices across a range of Datadog products.</p>
            <p>This e-learning module is available as a Just-in-time, self-paced, and focused learning approach for all team members.</p>
            <p>All training sessions will be on a "First come first serve basis".</p>
            <p><strong>How to register for the Datadog sessions?</strong></p>
            <ol>
                <li>Open the attached file titled "datadog_sessions".</li>
                <li>Select the course which you are interested to attend.</li>
                <li>Click on the specific course you would like to learn, and it will direct you to the DataDog web page.</li>
                <li>You will find details of the course you selected such as date, time, hours of session, and what you will learn.</li>
                <li>Under the Register tab, fill in your details:</li>
                <ul>
                    <li>First Name: Annie</li>
                    <li>Last Name: Lawrence</li>
                    <li>Business Email: <a href="mailto:Annie.Lawrence@ideas.com">annie.lawrence@ideas.com</a></li>
                    <li>Company: IDeas</li>
                    <li>Job Title: Human Resource</li>
                    <li>Country: India</li>
                </ul>
                <li>Post filling in details, click on "Register".</li>
                <li>You will receive a confirmation email on your business email id.</li>
                <li>In case you cannot attend the session, you can cancel your registration.</li>
                <li>Once you register for any training session, do share an email with <a href="mailto:Shivani.Gupte@ideas.com">Shivani.Gupte@ideas.com</a>.</li>
                <li>Post completing your training, share a screenshot of the completed training with <a href="mailto:Shivani.Gupte@ideas.com">Shivani.Gupte@ideas.com</a> (Email is mandatory as we need to track the number of team members using this platform and completing the training).</li>
            </ol>
            <p>Stay tuned for more information. In case of any queries feel free to reach out to <a href="mailto:Shivani.Gupte@ideas.com">Shivani.Gupte@ideas.com</a>.</p>
        </div>
    </body>
    </html>

    """

    # Paths to the attachments
    html_attachment = r"index.html"  # Use an absolute path or relative to the current directory
    # image_attachment = r"template.png"  

    # Check if both attachments exist
    if not os.path.exists(html_attachment):
        print(f"HTML attachment file not found: {html_attachment}")
        return
    # if not os.path.exists(image_attachment):
    #     print(f"Image attachment file not found: {image_attachment}")
    #     return
    
    # Prepare the boundary string
    boundary = "===============boundary_string==============="  # This needs to be unique and consistent
    
    # Start building the EML content
    eml_content = f"X-Unsent: 1\n"
    eml_content += f"From: {sender}\n"
    eml_content += f"To: {recipients_str}\n"
    eml_content += f"Subject: {subject}\n"
    eml_content += "Thread-Index: AQHbJEvWJEkmFcrfC0OKS6bNxDsJEQ==\n"
    eml_content += f"Date: {os.popen('date /T').read().strip()} {os.popen('time /T').read().strip()}\n"  # Current date and time
    eml_content += "Message-ID: <dummy-message-id@example.com>\n"
    eml_content += "Content-Language: en-US\n"
    eml_content += f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\n"
    eml_content += "MIME-Version: 1.0\n\n"

    # Add plain text part
    eml_content += f"--{boundary}\n"
    eml_content += "Content-Type: text/plain; charset=\"iso-8859-1\"\n"
    eml_content += "Content-Transfer-Encoding: quoted-printable\n\n"
    # eml_content += f"{plain_body}\n\n"

    # Add HTML part
    eml_content += f"--{boundary}\n"
    eml_content += "Content-Type: text/html; charset=\"iso-8859-1\"\n"
    eml_content += "Content-Transfer-Encoding: quoted-printable\n\n"
    eml_content += html_body + "\n\n"

    # Add attachments
    for attachment in [html_attachment]:
        filename = os.path.basename(attachment)
        encoded_content = encode_file_to_base64(attachment)
        
        if encoded_content is None:
            print(f"Failed to encode the attachment: {attachment}")
            return
        
        # Infer content type based on file extension
        if filename.endswith('.html'):
            content_type = "text/html"
        elif filename.endswith('.png'):
            content_type = "image/png"
        else:
            content_type = "application/octet-stream"  # Default for binary attachments
        
        eml_content += f"--{boundary}\n"
        eml_content += f"Content-Type: {content_type}; name=\"{filename}\"\n"
        eml_content += "Content-Transfer-Encoding: base64\n"
        eml_content += f"Content-Disposition: attachment; filename=\"{filename}\"\n\n"
        eml_content += f"{encoded_content}\n\n"

    # End the multipart message
    eml_content += f"--{boundary}--\n"
    
    # Write the .eml file
    eml_file_path = os.path.abspath("email_with_attachment.eml")

    try:
        with open(eml_file_path, "w", encoding='utf-8') as eml_file:
            eml_file.write(eml_content)
        print(f"EML file created successfully at {eml_file_path}")
    except Exception as e:
        print(f"Error writing the EML file: {e}")
        return

    # Try to open the .eml file
    try:
        os.startfile(eml_file_path)
    except Exception as e:
        print(f"Failed to open the EML file: {e}")

def main():
    print("Starting main()...")
    extract_info()
    htmlcreate()
    create_draft_email_with_attachment()
    print("Finished main()")

if __name__ == "__main__":
    main()
