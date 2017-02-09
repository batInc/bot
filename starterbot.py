import os
import time
from slackclient import SlackClient
import openweather
import pyowm


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
OPEN_WEATHER_TOKEN = os.environ.get("OPEN_WEATHER_TOKEN")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

owm = pyowm.OWM(OPEN_WEATHER_TOKEN)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if 'weather' in command:
	    w_dict = weather_parse()
	    weather = str(w_dict.get('temp'))
	    reponse = "The weather is Toronto is " + weather
	    print response
		
    else:
	    response = command
		
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def weather_parse():
    observation = owm.weather_at_place('Toronto, CA')
    weather = observation.get_weather()
    return weather.get_temperature('celcius')

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")