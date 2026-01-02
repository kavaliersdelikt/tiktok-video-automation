from groq import Groq
from moviepy.editor import *
import whisper
import yt_sc as yut
import VoiceRSSWebAPI
import random
import base64
import time as tm
import json
import shutil
import os

os.system('cls')
banner = '''    
██╗░░██╗██╗░░██╗░█████╗░███╗░░██╗███╗░░██╗██╗░░░██╗
╚██╗██╔╝╚██╗██╔╝██╔══██╗████╗░██║████╗░██║╚██╗░██╔╝
░╚███╔╝░░╚███╔╝░███████║██╔██╗██║██╔██╗██║░╚████╔╝░
░██╔██╗░░██╔██╗░██╔══██║██║╚████║██║╚████║░░╚██╔╝░░
██╔╝╚██╗██╔╝╚██╗██║░░██║██║░╚███║██║░╚███║░░░██║░░░
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚══╝░░░╚═╝░░░
               github.com/francool57
        \n'''
print(banner)
starttime = tm.time()

from moviepy.config import change_settings
with open('settings.json', 'r') as f:
    data = json.load(f)
    path = data['path']
    groc_api_key = data['groc_api_key'] # Groc API key: https://console.groq.com/keys
    voicerss_api = data['voicerss_api'] # VoiceRSS API key: https://www.voicerss.org/
    watermark_text = data.get('watermark_text', '')
    watermark_position = data.get('watermark_position', 'bottom_right')

def _prompt_api_key(label, current_value, url_hint):
    """Ask for an API key if missing to avoid blank Bearer headers."""
    if current_value and current_value.strip():
        return current_value.strip()
    print(f"{yut.Bcolors.RED}{label} is missing. Get one at {url_hint}.{yut.Bcolors.END}")
    entered = input(f"Enter {label} (or press Enter to abort): ").strip()
    if not entered:
        print(f"{yut.Bcolors.RED}Cannot continue without {label}.{yut.Bcolors.END}")
        exit(1)
    return entered

groc_api_key = _prompt_api_key("Groq API key", groc_api_key, "https://console.groq.com/keys")
voicerss_api = _prompt_api_key("VoiceRSS API key", voicerss_api, "https://www.voicerss.org/")

# Groq client upfront (used for hook suggestions and story)
client = Groq(
    api_key=groc_api_key,
)

audio_file_mp3 = "story_audio.mp3"
video_file_mp4 = "../fullyoutube.mp4"
hookfile = "hookaudio.mp3"

# Ask for video mode
print('\n=== VIDEO MODE SELECTION ===')
print('1) 2-PART VIDEO (Story continues in Part 2, each ~1 minute)')
print('2) 1-PART VIDEO (Complete story in one video, ~1 minute)\n')
video_mode = input('Select mode (1 or 2): ').strip()
while video_mode not in ['1', '2']:
    video_mode = input('Invalid choice. Please enter 1 or 2: ').strip()

# Offer AI-generated hook suggestions
print('\n=== HOOK GENERATOR ===')
use_ai_hook = input('Generate 5 viral hooks for me? (y/n): ').strip().lower()
suggested_hooks = []
if use_ai_hook == 'y':
    try:
        hook_resp = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": """Generate 5 different first lines for a short scary Reddit-like story. 
Each line must be viral, innovative, attention-grabbing, under 20 words, and avoid clichés. 
Return them as a numbered list (1-5). Do not repeat ideas.""",
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.9,
        )
        raw = hook_resp.choices[0].message.content
        for line in raw.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Strip leading numbering like "1." or "1)"
            if len(line) > 2 and line[0].isdigit() and (line[1] in ['.', ')']):
                line = line[2:].strip()
            suggested_hooks.append(line)
        # Keep top 5
        suggested_hooks = suggested_hooks[:5]
    except Exception as e:
        print(f"{yut.Bcolors.RED}Hook generation failed: {e}{yut.Bcolors.END}")

if suggested_hooks:
    print('\nPick one of these hooks:')
    for idx, hook in enumerate(suggested_hooks, 1):
        print(f"{idx}) {hook}")
    choice = input('Select 1-5 or press Enter to write your own: ').strip()
    if choice in ['1','2','3','4','5'] and int(choice) <= len(suggested_hooks):
        storyhook = suggested_hooks[int(choice)-1]
    else:
        storyhook = input('Write your own hook:\n> ')
else:
    storyhook = input('\nCreate a first line for your story.\nShould be similar to: "I got abandoned in a forest by my family, but i got revenge on them"\n> ')

path_mgk = shutil.which("magick") 
if path_mgk is None:
    path_mgk = shutil.which("convert")
if path_mgk is None:
    print(f"{yut.Bcolors.RED}ImageMagick not found. Install via build.sh or apt-get install imagemagick{yut.Bcolors.END}")
    exit()
change_settings({"IMAGEMAGICK_BINARY": path_mgk})

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Select video source
print('\n=== VIDEO SOURCE ===')
custom_url = input('Paste a YouTube URL (recommended) or press Enter for auto Minecraft search: ').strip()
custom_search = ''
if not custom_url:
    custom_search = input('Custom search term or Enter for default "minecraft parkour gameplay no copyright 4k": ').strip()
    if not custom_search:
        custom_search = 'minecraft parkour gameplay no copyright 4k'

try:
    if custom_url:
        yut.Download(url=custom_url)
    else:
        yut.Download(search=custom_search)
except BaseException as e:
    print(f"{yut.Bcolors.RED}Video download failed: {str(e)}. Falling back...{yut.Bcolors.END}")
    if custom_url:
        yut.Download(search='minecraft parkour gameplay no copyright 4k')
    else:
        yut.Download(search=custom_search)

# Generate story based on selected mode
if video_mode == '1':  # 2-Part mode
    # Generate Part 1 (cliffhanger)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'''Generate Part 1 of a 2-part scary reddit-like story from first person perspective.
                The story should be based on this hook: \"{storyhook}\", but don't include this exact phrase.
                This Part 1 should be around 150 words.
                The story must be based on realistic events.
                Start with a gripping hook that shows the most unsettling moment.
                END Part 1 with a CLIFFHANGER that makes viewers want to see Part 2.
                Write as a natural essay, no meta-commentary.''',
            }
        ],
        model="llama-3.1-8b-instant",
    )
    response_part1 = chat_completion.choices[0].message.content
    print(f'{yut.Bcolors.GREEN}Part 1 text was generated{yut.Bcolors.END}')
    
    # Generate Part 2 (resolution)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'''Generate Part 2 of a scary reddit story. This continues from Part 1.
                Part 1 was: {response_part1}
                
                Now write Part 2 (around 150 words) that:
                - Continues directly from the cliffhanger
                - Reveals what happens next
                - Provides a satisfying conclusion
                - Has a good ending
                Write as a natural continuation, no "Part 2" labels or meta-commentary.''',
            }
        ],
        model="llama-3.1-8b-instant",
    )
    response_part2 = chat_completion.choices[0].message.content
    print(f'{yut.Bcolors.GREEN}Part 2 text was generated{yut.Bcolors.END}')
else:  # 1-Part mode
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'''Generate a scary reddit-like story from first person perspective.
                The story should be based on: \"{storyhook}\", but don't include this exact phrase.
                This story should be around 170 words (for ~1 minute of speech).
                The story must be based on realistic events.
                Start with a short hook showing the most unsettling part.
                The story should have a complete, satisfying ending.
                Write as a natural essay, no meta-commentary.''',
            }
        ],
        model="llama-3.1-8b-instant",
    )
    response = chat_completion.choices[0].message.content
    print(f'{yut.Bcolors.GREEN}Text was generated{yut.Bcolors.END}')

#tts
voicer = random.choice(['Mike','John','Amy','Linda'])

if video_mode == '1':  # 2-Part mode - create audio for both parts
    # Part 1 audio
    voice = VoiceRSSWebAPI.speech({  
        'key': voicerss_api,
        'hl': 'en-us',
        'v': voicer, 
        'src': response_part1,
        'r': '0',
        'c': 'mp3',
        'f': '44khz_16bit_stereo',
        'ssml': 'false',
        'b64': 'true'
    })
    wav_file = open((path+audio_file_mp3), "wb")   
    decode_string = base64.b64decode(voice['response'])
    wav_file.write(decode_string)
    wav_file.close()
    print(f'{yut.Bcolors.GREEN}Part 1 audio was created{yut.Bcolors.END}')
    
    # Part 2 audio
    voice_part2 = VoiceRSSWebAPI.speech({  
        'key': voicerss_api,
        'hl': 'en-us',
        'v': voicer, 
        'src': response_part2,
        'r': '0',
        'c': 'mp3',
        'f': '44khz_16bit_stereo',
        'ssml': 'false',
        'b64': 'true'
    })
    wav_file2 = open((path+"story_audio_part2.mp3"), "wb")   
    decode_string2 = base64.b64decode(voice_part2['response'])
    wav_file2.write(decode_string2)
    wav_file2.close()
    print(f'{yut.Bcolors.GREEN}Part 2 audio was created{yut.Bcolors.END}')
else:  # 1-Part mode
    voice = VoiceRSSWebAPI.speech({  
        'key': voicerss_api,
        'hl': 'en-us',
        'v': voicer, 
        'src': response,
        'r': '0',
        'c': 'mp3',
        'f': '44khz_16bit_stereo',
        'ssml': 'false',
        'b64': 'true'
    })
    wav_file = open((path+audio_file_mp3), "wb")   
    decode_string = base64.b64decode(voice['response'])
    wav_file.write(decode_string)
    wav_file.close()
    print(f'{yut.Bcolors.GREEN}Audio was created as story_audio.mp3{yut.Bcolors.END}')

voice = VoiceRSSWebAPI.speech({
    'key': voicerss_api,
    'hl': 'en-us',  
    'v': voicer,
    'src': storyhook,
    'r': '0',
    'c': 'mp3',
    'f': '44khz_16bit_stereo',
    'ssml': 'false',
    'b64': 'true'
})                              # Hook voiceover

wav_file = open((path+hookfile), "wb")
decode_string = base64.b64decode(voice['response'])
wav_file.write(decode_string)
print(f'{yut.Bcolors.GREEN}Audio was created as hookaudio.mp3{yut.Bcolors.END}')
wav_file.close()

def video_create():
    # Load the audio file
    audio = AudioFileClip(path + audio_file_mp3)
    audio2 = AudioFileClip(path + hookfile)
    print(f'{yut.Bcolors.BLUE}Audio was added{yut.Bcolors.END}')


    # Load the video file
    video = VideoFileClip(path + video_file_mp4)
    # Calculate the center coordinates of the video
    crop_x = 1980 / 2
    crop_y = 1280 / 2

    # Resize the video to TikTok format (720x1280)
    video = video.resize((1980, 1280))
    video_resized = video.crop(
                            x_center = crop_x, 
                            y_center = crop_y, 
                            width=720, 
                            height=1280
                            ).set_duration(audio.duration+audio2.duration)

    print(f'{yut.Bcolors.BLUE}Video was re-sized{yut.Bcolors.END}')

    # Attach the audio to the video
    mixed = CompositeAudioClip([audio2, audio.set_start(audio2.duration)]).set_fps(44100)
    video_with_audio = video_resized.set_audio(mixed)

    # Define the text to display, one word at a time
    clips = []
    model_size = "base"

    # stt and word division (CPU mode for Codespaces)
    print(f'{yut.Bcolors.CYAN}Loading Whisper model...{yut.Bcolors.END}')
    model = whisper.load_model(model_size)
    result = model.transcribe(path+audio_file_mp3, word_timestamps=True)
    result2 = model.transcribe(path+hookfile, word_timestamps=True)
    print(f'{yut.Bcolors.CYAN}Whisper model loaded{yut.Bcolors.END}')

    # Process hook words
    for segment in result2['segments']:
        for word_data in segment.get('words', []):
            word_text = word_data['word'].strip()
            start_time = word_data['start']
            end_time = word_data['end']
            duration = end_time - start_time
            
            txt = TextClip(word_text, 
                            font='Arial-Black',
                            fontsize=70, 
                            color='red', 
                            size=(1080, 250), 
                            stroke_color='black', 
                            stroke_width=2).set_position('center').set_duration(duration).set_start(start_time)
            clips.append(txt)
    print(f'{yut.Bcolors.BLUE}Hook was appended as clips{yut.Bcolors.END}')
    
    # Add each word as a separate TextClip
    for segment in result['segments']:
        for word_data in segment.get('words', []):
            word_text = word_data['word'].strip()
            start_time = word_data['start']
            end_time = word_data['end']
            duration = end_time - start_time
            
            txt_clip = TextClip(word_text, 
                                font='Arial-Black',
                                fontsize=70, 
                                color='white', 
                                size=(1080, 250), 
                                stroke_color='black', 
                                stroke_width=2).set_position('center').set_duration(duration).set_start(start_time+audio2.duration)
            clips.append(txt_clip)
    print(f'{yut.Bcolors.BLUE}Text was appended as clips{yut.Bcolors.END}')

    # Add watermark if configured
    if watermark_text:
        # Calculate watermark position
        if watermark_position == 'bottom_right':
            watermark_pos = (540, 1200)  # Bottom right corner
        elif watermark_position == 'bottom_left':
            watermark_pos = (20, 1200)
        elif watermark_position == 'top_right':
            watermark_pos = (540, 50)
        elif watermark_position == 'top_left':
            watermark_pos = (20, 50)
        else:
            watermark_pos = (540, 1200)  # Default to bottom right
        
        watermark = TextClip(watermark_text,
                            font='Arial-Bold',
                            fontsize=30,
                            color='white',
                            stroke_color='black',
                            stroke_width=1.5).set_position(watermark_pos).set_duration(audio.duration+audio2.duration).set_opacity(0.7)
        clips.append(watermark)
        print(f'{yut.Bcolors.GREEN}Watermark added: {watermark_text}{yut.Bcolors.END}')

    # Overlay the text clips on the video
    video_with_text = CompositeVideoClip([video_with_audio] + clips)

    size_vid = str(video_with_text.size).replace(', ','x')
    print(f'{yut.Bcolors.CYAN}Video has {size_vid} dimensions{yut.Bcolors.END}')
    # Export the final video
    video_with_text.write_videofile(
        f"{path}final_tiktok_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        audio=True,
        audio_fps=44100,
    )

if __name__ == '__main__':
    if video_mode == '1':  # 2-Part mode - create both videos
        print(f'\n{yut.Bcolors.CYAN}=== CREATING PART 1 ==={yut.Bcolors.END}')
        video_create()  # Creates Part 1
        
        # Now create Part 2
        print(f'\n{yut.Bcolors.CYAN}=== CREATING PART 2 ==={yut.Bcolors.END}')
        # Download another background video for Part 2
        try:
            yut.Download()
        except BaseException as e:
            print(f"{yut.Bcolors.RED}An error has occurred: ||{str(e)}||. Re-running...{yut.Bcolors.END}")
            yut.Download()
        
        # Temporarily swap audio files for Part 2
        import shutil as sh
        sh.move(path+audio_file_mp3, path+"story_audio_part1_backup.mp3")
        sh.move(path+"story_audio_part2.mp3", path+audio_file_mp3)
        
        video_create()  # Creates Part 2
        
        # Rename outputs
        sh.move(path+"final_tiktok_video.mp4", path+"final_tiktok_video_PART2.mp4")
        sh.move(path+"story_audio_part1_backup.mp3", path+audio_file_mp3)
        video_create()  # Re-create Part 1 with correct naming
        sh.move(path+"final_tiktok_video.mp4", path+"final_tiktok_video_PART1.mp4")
        
        print(f'\n{yut.Bcolors.GREEN}✓ PART 1: video_audio/final_tiktok_video_PART1.mp4{yut.Bcolors.END}')
        print(f'{yut.Bcolors.GREEN}✓ PART 2: video_audio/final_tiktok_video_PART2.mp4{yut.Bcolors.END}')
    else:  # 1-Part mode
        video_create()
        print(f'\n{yut.Bcolors.GREEN}✓ VIDEO: video_audio/final_tiktok_video.mp4{yut.Bcolors.END}')
    
    endtime = tm.time()
    timee = int(endtime-starttime)
    print(f'\n{yut.Bcolors.CYAN}Elapsed time: {timee}s{yut.Bcolors.END}')
else: 
    print('I have no idea why it did not run')
    exit()