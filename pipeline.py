
from deepsearch_module import run_search_module
from script_module import run_script_module
from audio_module import run_audio_module
from video_module import run_video_module

if __name__ == "__main__":
    query = input("请输入要生成视频的关键词：").strip()
    if not query:
        raise ValueError("关键词不能为空")

    sections_json, images = run_search_module(query)

    script_list, script_json = run_script_module(sections_json)

    audio_files = run_audio_module(script_json)

    output_video = run_video_module(script_json)