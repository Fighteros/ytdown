import json
import os
import re
from datetime import datetime


import yt_dlp


# 1- Request info
# 2- Get List of quality for a video
# 3- extract download links and sanitize for printing

def format_selector(is_audio, info):
    """
    Select the best video and the best audio that won't result in an mkv
    :param isAudio : Boolean:
    :return dicit :
    """

    formats = info.get('formats')
    video_list = [x for x in formats if x.get('filesize') is not None and x.get('vcodec') != 'none']
    best_audio = [x for x in formats if
                  x.get('filesize') is not None and x.get('acodec') != 'none' and x.get('vcodec') == 'none']

    if not is_audio:
        # List video list with quality
        for i, x in enumerate(video_list):
            if x.get('video_ext') == 'mp4':
                # Can create a function for get size for better unit showing (to be done)
                print(
                    f"({i + 1}) {x.get('format_note')}@{x.get('vcodec')} - {x.get('audio_ext')} ({round(float(x.get('filesize') / (1024 * 1024)), 2)} Mbs)")

        video_quality = int(input('Choose quality: ')) - 1

        # Find suitable audio for the selected video
        audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[video_list[video_quality].get('ext')]
        best_audio = next(f for f in formats if (
                f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('ext') == audio_ext))

        return {"video_url": video_list[video_quality], "audio_url": best_audio}

    else:
        for i, x in enumerate(best_audio):
            print(
                f"({i + 1}) {x.get('format_note')}@{x.get('acodec')} - {x.get('video_ext')} ({round(float(x.get('filesize') / (1024 * 1024)), 2)} Mbs)")

        audio_qaulity = int(input('Choose quality: ')) - 1

        toDownload = best_audio[audio_qaulity]

        format_for_opts = str(toDownload.get('format_id'))

        output_name = info.get('title') + "." + toDownload.get('ext')

        ydl_opts = {
            'format': format_for_opts,
            'outtmpl': output_name
        }


        return {"base_url": info.get('original_url'), "ydl_opts": ydl_opts}

        # # Download the specific format
        # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #     ydl.download(info.get('original_url'))

# Returns a json of the info for the video requested
def get_info(video_url):

    ydl_opts = {}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

        return json.dumps(ydl.sanitize_info(info))

def part_vid():
    print("""Cut video ? [y/n]""")
    answer = input('')
    if answer.lower() == 'y':
        return True
    else:
        return False

def isAudio():
    print('Download audio only? [y/n]')
    answer = input('')
    if answer.lower() == 'y':
        return True
    else:
        return False


def download(is_audio, format_dict,cut_video = None,  info = None, start='00:00:00', end=''):

    video_link = format_dict.get('video_url').get('url')
    audio_link = format_dict.get('audio_url').get('url')
    yt_title = info.get('title')
    title = re.sub(r'[\/:*?"<>|]', "", yt_title)
    video_ext = info.get('ext')

    if is_audio:
        # Download the specific format
        with yt_dlp.YoutubeDL(format_dict.get('ydl_opts')) as ydl:
            ydl.download(info.get('original_url'))

    if end != '':
        t1 = datetime.strptime(start, "%H:%M:%S")
        t2 = datetime.strptime(end, "%H:%M:%S")
        duration = t2 - t1
        os.system(
            f"ffmpeg -ss {start} -i \"{video_link}\" -ss {start} -i \"{audio_link}\"  -map 0:v -map 1:a -t {duration.total_seconds()} -c:v libx264 -c:a aac \"{title}.mp4\" ")
    else:
        os.system(
            f"ffmpeg -ss {start} -i \"{video_link}\" -ss {start} -i \"{audio_link}\"  -map 0:v -map 1:a  -c:v libx264 -c:a aac \"{title}.mp4\" ")


def main():
    video_url = input('Video URL: ')

    is_audio = isAudio()
    cut_video = part_vid() if not is_audio else None


    info_data = json.loads(get_info(video_url))

    format_dict = format_selector(is_audio, info_data)

    if is_audio:
        download(is_audio, format_dict, info=info_data)

    if cut_video:
        start = input("Start: ")
        end = input("end: ")
        download(is_audio, format_dict, cut_video, info=info_data, start=start, end=end)
    else:
        download(is_audio, format_dict, info=info_data)







if __name__ == '__main__':
    main()
