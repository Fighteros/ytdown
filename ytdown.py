#!/usr/bin/python
import os
from datetime import datetime
import re
import youtube_dl

# open run from dir
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


# Get the best audio quality by default
def get_best_audio(list_of_audio):
    max_quality = 0
    for m in list_of_audio:
        if int(m) > max_quality:
            max_quality = int(m)
    return max_quality


# Get video internal links (stream links and quality build)
def get_intern_links(url):
    info = youtube_dl.YoutubeDL()
    list_of_formats = info.extract_info(url, download=False, )
    audio_list = {}
    for x, i in enumerate(list_of_formats['formats']):

        print(f"({x + 1}) {i['format']} {i['ext']} {i['format_note']}")
        if (i['ext'] == 'webm' or i['ext'] == 'm4a') and (
                i['format'] == '251 - audio only (tiny)' or i['format'] == '250 - audio only (tiny)' or i[
            'format'] == '140 - audio only (tiny)'):
            audio_list[i['format'].split(' ')[0]] = i["url"]

    video_quality = input('Video Quality:')
    try:
        audio_url = audio_list[str(get_best_audio(audio_list))]
        video_url = list_of_formats['formats'][int(video_quality) - 1]['url']
        video_title = info.extract_info(url, download=False, )['title']
        return [audio_url, video_url, video_title]
    except Exception as e:
        print('Sorry error occurred check the log file')
        open('log', 'a+').write(str(e))


# combine and download video
def combine_streams(audio_link, video_link, title, start='00:00:00', end=''):
    new_title = re.sub(r'[\/:*?"<>|]', "", title)
    if end != '':
        t1 = datetime.strptime(start, "%H:%M:%S")
        t2 = datetime.strptime(end, "%H:%M:%S")
        duration = t2 - t1
        os.system(
            f"ffmpeg -ss {start} -i \"{video_link}\" -ss {start} -i \"{audio_link}\"  -map 0:v -map 1:a -t {duration.total_seconds()} -c:v libx264 -c:a aac \"{new_title}.mp4\" ")
    else:
        os.system(
            f"ffmpeg -ss {start} -i \"{video_link}\" -ss {start} -i \"{audio_link}\"  -map 0:v -map 1:a  -c:v libx264 -c:a aac \"{new_title}.mp4\" ")
        # print(
        #     f"ffmpeg -v info -stats -ss {start} -i \"{video_link}\" -ss {start} -i \"{audio_link}\"  -map 0:v -map 1:a  -c:v libx264 -c:a aac \"{new_title}.mp4\" ")


def part_vid():
    print("""
Cut video ?
    
    [y] yes          [n] no
    """)
    answer = input('')
    if answer.lower() == 'y':
        return True
    else:
        return False


# ffmpeg -ss 00:18 -i $video_url -ss 00:18 -i $audio_url -map 0:v -map 1:a -t 35 -c:v libx264 -c:a aac romanticHomicide.mp4
def main():
    url = input('URL: ')
    opts = part_vid()
    list_of_links = get_intern_links(url)
    if opts:
        start = input("Start: ")
        end = input("end: ")
        combine_streams(list_of_links[0], list_of_links[1], list_of_links[2], start, end)
    else:
        combine_streams(list_of_links[0], list_of_links[1], list_of_links[2])


main()
