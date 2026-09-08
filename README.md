# Evil-Ai-dis
A transparent, unfiltered AI Discord bot designed to operate in a specific channel.

In-channel operation: Responds without prefixes or commands

0% Refuse Response: Direct, uncensored answers to any question

Context memory: Maintains chat context in real time

The bot only listens to a specific Discord channel and answers questions using the AI model loaded locally in LM Studio via its local API server (compatible with OpenAI APIs)
Open LM Studio and load the model you want to use, Ministral 7B Heretic v2 l1 was used for testing but it depends heavily on the hardware of the machine used.
Start the local server: setting > Local Mode API > Local API server > ON / Running
Note down the displayed address which will later go into the LM_STUDIO_URL section inside the .env file (by default http://localhost:1234). Leave LM Studio open and the server running while the bot is running.

Create the bot on Discord: https://discord.com/developers/applications > New Application.
In Privileged Gateway Intents, enable Message Content Intent.
Copy the bot Token (Reset Token if you don't see it), this will also go inside the .env file.
OAuth2 > URL Generator:
Minimum permissions: Send Messages, Read Message History, View Channels
Open the generated URL and invite the bot to your server.

Find the channel ID
Discord: User Settings > Advanced > Developer Mode > ON.
Right-click on the channel where you want the bot to respond > Copy Channel ID.

Open .env and fill in the fields as requested with the previously copied strings.
! In the LM_STUDIO_URL section, you need to enter the previously copied localhost link followed by /chat/completions 
e.g., http://localhost:1234/v1/chat/completions

bash
pip install -r requirements.txt
python evilai.py

If everything is configured correctly, in the terminal you will see:

Bot connected as YourBot#1234
Listening on channel ID ...

Now write a question in the configured Discord channel: the bot will forward it to LM Studio and publish the answer.

Notes
The bot maintains a small conversation history per channel (by default the last 10 question/answer pairs) so the model has a minimum of context. You can adjust it with MAX_HISTORY_MESSAGES in the .env.
You can customize the model behavior by modifying SYSTEM_PROMPT in the .env file
The PC on which LM Studio runs must remain on and with the server running as long as the bot is active: the bot runs on the same machine (or on a machine that can reach that address on the local network).
The bot answers any question asked in the chosen channel, to make it answer only when mentioned, changes to the main python file are required which will be implemented with the next update of the repository.
