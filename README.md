# Slack Genie HTTP

A minimal HTTP-based Slack bolt implementation built with **FastAPI** to interact with Databricks Genie API. The app listens for Slack Events API. Forwards them to Databricks Genie API via Fast API and returns the response. FastAPI brokers the communication to and from Slack and Genie API.


## Features
- Slack Events Handler
- Fast API backend (async support)
- Integration with Databricks Genie endpoint
- Compatible with local development and Cloud Deployment (in this case, tested with Heroku)

# Getting Started
---
## Local Deployment for Testing
Start with local and make sure it runs ok. This is just for testing.

### 1. Clone the repo
```
git clone https://github.com/smakubi/slack-genie-http.git
cd slack-genie-http
```

### 2. Create a .env file
```
DATABRICKS_HOST=
DATABRICKS_TOKEN=
FORMAT_TABLES=true
MAINTAIN_CONTEXT=true
MAX_RETRIES=10
RETRY_INTERVAL=5
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=
SLACK_SIGNING_SECRET=
SPACE_ID=
ENV=production
```
Do not commit .env to source control.

### 3. Create and Activate Virtual Environment
```
python -m venv myenv
source myenv/bin/activate
```
### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Run locally
```
uvicorn app:app --reload
```
This starts the FastAPI server on http://localhost:8000.

### 6. Test with ngrok (for Slack)
If you don't have ngrok. Install and create an account and add your authtoken to the default ngrok.yml configuration file.
 ([https://ngrok.com/](https://dashboard.ngrok.com/get-started/setup/macos)). 

 Install:
 ```
brew install ngrok
```

Adding Authtoken (this is one time only operation):
```
ngrok config add-authtoken your-auth-token
```
Now open another terminal and run ngrok:
```
ngrok http 8000
```
This will give you a forwarding URL. Then Update your Slack app to point the callback URL to your ngrok forwarding URL.

---
## Cloud Deployment (Heroku) for Production
This is for production. Make sure you are in the project directory.
### 1. Install Heroku CLI
Here's the link: https://devcenter.heroku.com/articles/heroku-cli

In MacOS you can use Homebrew:
```
brew install heroku/brew/heroku
```
Ensure you've installed:
```
heroku --version
```

Log into Heroku:
```
heroku login
```

### 2. Create Heroku App
```
heroku create your-fastapi-app
```
Add files to and commit to Heroku:
```
git add .
git commit -m "initial heroku commit"
```

Connect to Heroku:
```
heroku git:remote -a your-fastapi-app
```

Deploy to Heroku:
```
git push heroku main
```

Set secrets and configs with:
```
heroku config:set DATABRICKS_HOST=https://example.databricks.com/ \
DATABRICKS_TOKEN=your-databricks-token \
FORMAT_TABLES=true \
MAINTAIN_CONTEXT=true \
MAX_RETRIES=10 \
RETRY_INTERVAL=5 \
SLACK_BOT_TOKEN=xoxb-.......... \
SLACK_CHANNEL_ID=slack-channel-id \
SLACK_SIGNING_SECRET=your-slack-bot-signing-secret \
SPACE_ID=your-genie-space0id \
ENV=production
```

Now check that configs are set with:
```
heroku config
```

Your fastapi app should now be running.
Check to see the routes:
```
https://your-heroku-fastapi-app-url.com/docs
```
Make note of the /slack/events endpoint:
```
https://your-heroku-fastapi-app-url.com/api/v1/slack/events
```
Go ahead and update your slack app request URL to use the above endpoint. So that slack can events to your app.


---
## Slack App
### 1. Create Slack App
- Go to https://api.slack.com/apps
- Click “Create New App”
- Choose “From an app manifest”
- Select your workspace
- Paste your manifest.yaml contents into the form
- Click “Next” → Review → Create

### 2. Update Slack Request URL
- Go back to: https://api.slack.com/apps/. Select the app you created "GENIE"
- Click Event Subscriptions and update the Request URL with your slack/events endpoint URL from earlier (ie: https://your-heroku-fastapi-app-url.com/api/v1/slack/events for Heroku) or (your-ngrok-url.com/api/v1/slack/events for Local)
- Save Changes.

### 3. Add Slack App to Your Workspace
- On the app page select "OAuth & Permissions"
- Under OAuth Tokens click on "Install to <Your Workspace Name>
- Optionally select a channel to install to and click Allow
- This should generate:
```
   User OAuth Token: xoxp-..........
   Bot User OAuth Token: xoxb-.......
```
- Take note of the above.

### 4. Now update Secrets and Variables in .env and in Heroku env
- Open .env
- Add:
```
   SLACK_BOT_TOKEN (Slack Bot User OAuth Token) from above (xoxb NOT xoxp). It should start with xoxb-
   SLACK_CHANNEL_ID: Default channel ID you added above 
   SLACK_SIGNING_SECRET: On the main app page. Click on "Basic Information". Under "Signing Secret" click "Show". Copy Signing Secret.
```

- Next Update these configs on Slack Env too with:
```
   heroku config:set SLACK_BOT_TOKEN=xoxb-.......... \
   SLACK_CHANNEL_ID=slack-channel-id \
   SLACK_SIGNING_SECRET=your-slack-bot-signing-secret \
```

If prompted re-install your app.