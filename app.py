import streamlit as st
from video import ThethaVideoWrapper
from nlp import NLPWrapper
import json
import re
import os
from dotenv import load_dotenv
load_dotenv(".env")

# Default values for the smart contract
sc = {"player_uri":"", "playback_uri":"", "swear_count": 0,
      "topics": dict(), "safety_score": 1.0, "languages": []
    }

def _extractListFromString(string):
    langs_list = []
    single_quote_no_spaces = "\[(\'\w+\'\,?)+\]"
    single_quote_with_spaces = "\[(\'\w+\'\,?\ )+(\'\w+\')\]"
    double_quote_no_spaces = "\[(\"\w+\"\,?)+\]"
    double_quote_with_spaces = "\[(\"\w+\"\,?\ )+(\"\w+\")\]"
    if re.search(single_quote_no_spaces, string) or re.search(double_quote_no_spaces, string):
        langs_list = string[1:-1].split(',')
        langs_list = [el[1:-1] for el in langs_list]
        
    if re.search(single_quote_with_spaces, string) or re.search(double_quote_with_spaces, string):
        langs_list = string[1:-1].split(', ')
        langs_list = [el[1:-1] for el in langs_list]
    return langs_list

def _proccessText(nlp):
    swears, topics, langs, score = nlp.extractFeaturesFromText()
    if swears["count_swears"][0].isnumeric():
        sc["swear_count"] = int(swears["count_swears"][0])
    
    try:
        evald = eval(topics["sentiments"][0])
        if isinstance(evald, dict):
            sc["topics"] = evald
    except ValueError:
        pass
    
    langs_list = _extractListFromString(langs["language"][0])
    if len(langs_list) > 0:
        sc["languages"] = langs_list
    
    
    if score["score"][0].isnumeric():
        sc["swear_count"] = float(score["score"][0])

def app():
    st.set_page_config(page_title="Video Upload",
                       page_icon=":movie_camera:", layout="wide")
    st.title("Video Upload :clapper:")
    # Add a file uploader to allow the user to upload a video
    uploaded_file = st.sidebar.file_uploader('##### Upload a video :arrow_up_small:', type=[
                                              'mp4'], accept_multiple_files=False)
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            
            vid = uploaded_file.name
            with open(vid, mode='wb') as f:
                f.write(uploaded_file.read()) # save video to disk
            st_video = open(vid,'rb')
            nlp = NLPWrapper(os.getenv("OPENAI_KEY"), os.getenv("email"), os.getenv("pwd"))
            with st.spinner("Transcribing video... :mag_right::hourglass_flowing_sand:"):
                nlp.transcribeFake(vid)
            with st.spinner("Extracting features from video... :mag_right::hourglass_flowing_sand:"):
                _proccessText(nlp)
            
            thetaVideo = ThethaVideoWrapper(os.getenv('SA_ID'), os.getenv('SA_SECRET'), bytes_data)
            with st.spinner("Creating file url... :mag_right::hourglass_flowing_sand:"):
                thetaVideo.createUploadId()
            with st.spinner("Uploading file... :mag_right::hourglass_flowing_sand:"):
                thetaVideo.upload()
            with st.spinner("Transcoding... :mag_right::hourglass_flowing_sand:"):
                thetaVideo.transcode()
            with st.spinner("Waiting to finish uploading transcoded... :mag_right::hourglass_flowing_sand:"):
                thetaVideo.waitForPlaybackUrl()

            st.write(':paperclip:')
            st.write(f'{thetaVideo.player_url}')
            sc["player_uri"] = thetaVideo.player_url
            sc["playback_uri"] = thetaVideo.playback_url
            st.write(sc)
        except Exception as e:
            st.write("ERROR:", e)

# Run the Streamlit app
if __name__ == '__main__':
    app()