import anthropic
import time
import re
import os
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODE="TEST"
def get_top_artists(spotify, limit=10, time_range='long_term', print_top_artists=False):
    # Get the top tracks
    top_tracks = spotify.current_user_top_tracks(limit=limit, time_range=time_range)

    # Display the top tracks
    if print_top_artists:
        for idx, track in enumerate(top_tracks['items']):
            print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")

    toptracks_text = ""
    toptracks_list = []
    for idx, track in enumerate(top_tracks['items']):
        toptracks_text += f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}\n"
        toptracks_list.append(f"{track['name']} by {track['artists'][0]['name']}")

    return toptracks_text, toptracks_list


import anthropic
def get_ai_judgment(toptracks):
    if MODE == "DEV":
        time.sleep(3)
        judgment =  """1. You're probably a flannel-wearing, iced-coffee-sipping queer who thinks having a septum piercing is a personality trait. 2. You've definitely cried in a Subaru while listening to Tegan and Sara at least once in your life. 3. Your idea of "country music" is whatever plays at the local dive bar during happy hour. 4. You're still not over your high school emo phase, but now you disguise it as "indie rock appreciation." 5. You're the type to claim you have an "eclectic taste in music," but really, you just can't commit to a single genre or decide who you want to be."""
    else: 
        client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=ANTHROPIC_API_KEY,
        )
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0.75,
            system="I will give you a list of a persons top tracks on Spotify and you should come up with some funny and slightly mean generalizations about them based on their music taste. You should come up with 5 funny generalizations in a list. Starting with 1. The generalizations should be in second person. Just give me the list there is no need for an intro.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": toptracks
                        }
                    ]
                }
            ]
        )
        judgment =  message.content[0].text
    
    pattern = r'\d+\.\s*'

    # Split the text
    judgments = re.split(pattern, judgment.strip())
    # The first element will be empty because of the leading delimiter, so remove it
    judgments = [item for item in judgments if item]
    print(judgments)
    return judgments