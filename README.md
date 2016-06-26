# WhenIsMyBus
A simple alexa / amazon echo app to tell me when my busses are arriving.
I use this while getting ready for work or when I'm about to head downtown.

By default, asks about three stops near my house that I take often.
Using the "intent" functionality with Alexa, it can also allow other sets of stops
## Reuse
You are welcome to reuse this code.  
Please get and use your own API key. They are free at:  
https://developer.wmata.com/  
I left mine in the code but if lots of folks use it I'll have to take it out.  
So please be polite :)

### Resources
You will need to get a (free) developer setup with Amazon:  
https://developer.amazon.com/home.html
and an AWS account (also free for I think a million calls a month)  
https://console.aws.amazon.com/console/home?region=us-east-1  
note that you must select the us-east-1 region for Alexa skills  

### Then to use the code:  
**Code:**  
* Put in your own API key instead  
* Change the stop list in the default intent to the list of stops * and routes you want to query  
* If you want a custom intent, change the name and stop list for "north" to whatever you want. You can add more if you want, just be ready to add them to the intent schema below as well

**Lambda:**  
* Go to the AWS console and select "lambda"  
* Click "Create a Lambda function"  
* Skip selecting a blueprint  
* Select "python" as runtime  
* Paste in the whole .py file  
* Under "Role", select lambda_basic_execution  
* you may want to turn up the timeout since we're hitting an API (I use 6 seconds)  
* Click next  
* Click "event sources" on the top bar.  
* Click "add event source" and pick "Alexa Skills"  

*Keep this open since you'll need the ARN from the top right shortly*

**Alexa Skill:**
* Update the intent file to change the name of the custom intent
* Update the sample utterances to tell alexa what modifiers to map to your custom intent
* Go to developer.amazon.com and log in
* Click "alexa" on the top bar
* Click "add a new skill"
* For name, use "WhenIsMyBus"
* For invocation name use "when is my bus"
* Click next
* Paste the intent schema into the top box
* Paste the sample utterances into the bottom box
* Click save, it should build the model
* Click next.

*If you want to customize:*  
Change the list of stop IDs and route names to the ones that interest you.

That's it! Your echo should have the skill immediately. Just say:  
*Alexa, ask when is my bus*

## Possible future features:
* Checking for line disruptions to report with the times
* Set up account linking or Amazon Dynamo or a similar server to be able to save user info so a user could set their own stops via voice interface
* Building a better interpreter to allow phrases like “when is the next 64,” or staged queries
* Integrate with google maps API to get custom metro directions and next bus times
* Figure out what I'd need to do to integrate into Alexa proper
