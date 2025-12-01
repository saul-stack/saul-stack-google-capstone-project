# A.I Calendar Assistant Project


## Please read Write-Up for more detail, including agent architecture diagrams

[View the full project report (PDF)](Write-Up-1-12-25.pdf)


## Setup

### Pre-requisites

Before you begin, ensure you meet one of the following criteria:

    a. The developer has registered your Gmail account as a test user and provided a credentials file `credentials.json`

    b. The developer has provided you a service account `test-credentials.json`

and that you have the following installed on your system:

    - Python 3.14.0
  

You will also need an API key for each of the following:

    1.  Google Gemini API
    2.  Google Maps Weather API
    3.  Google Calendar API

#

### 1. Set up Python environment

1. Navigate to root directory 
   
        $ cd saul-stack-google-capstone-project

2. Create and activate Python virtual environment
   
        $ python -m venv virtual_env
        $ source ./virtual_env/bin/activate
   
3. Install Python dependencies
   
        $ pip install -r requirements.txt

#

### 2. Configure environment variables


1. Navigate to project root directory 

        $ cd saul-stack-google-capstone-project

2. Create environment file
   
        $ touch .env

3. Open `.env` and add the following lines:

        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS=TRUE
        GOOGLE_API_KEY=<your-gemini-api-key>        GOOGLE_MAPS_API_KEY=<your-google-maps-api-key>


#

### Authorizing Google Calendar API


#### Testing with a registered Google account:


1. Copy `credentials.json` to saul-stack-google-capstone-project/setup/


3. Add the following line to `.env`: 

        USE_SERVICE_ACCOUNT=FALSE

4. Run `configure_google_calendar_api.py` and open your web browser to grant permissions to the application
   
        $ cd setup
        $ python configure_google_calendar_api.py

#### Testing with a service account: 

1. Copy `test-credentials.json` to saul-stack-google-capstone-project/setup/
2. add the following line to .env: 

        USE_SERVICE_ACCOUNT=TRUE


This authenticates each calendar request using a service account instead of user OAuth.

## Running the application

        $ cd saul-stack-google-capstone-project/agents
        $ adk web

