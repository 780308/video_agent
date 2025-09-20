# video_module.py
import os
import json
import random
from glob import glob
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)
from PIL import Image

# Pillow 10+ 兼容
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:/Program Files/ImageMagick-7.1.2-Q16/magick.exe"})

# ========= 配置默认值 =========
FPS = 30
IMAGE_DURATION = 4    # 每张图显示时长
TITLE_DURATION = 2.0   # 标题帧时长
VIDEO_SIZE = (1280, 720)  # 输出分辨率（720p）
TITLE_BG = "title_bg.jpg"  # 标题背景图片
FADE_DURATION = 0.5   # 图片淡入淡出时长

# ========= 辅助函数 =========
def make_title_frame(title_text):
    """生成带水墨背景的标题帧"""
    if not os.path.exists(TITLE_BG):
        raise FileNotFoundError(f"未找到标题背景图: {TITLE_BG}")

    bg = ImageClip(TITLE_BG).resize(VIDEO_SIZE).set_duration(TITLE_DURATION)

    txt = TextClip(
        title_text, fontsize=70, color="black",
        font="SimHei", size=VIDEO_SIZE, method="caption"
    ).set_duration(TITLE_DURATION).set_position("center")

    return CompositeVideoClip([bg, txt])

def make_slideshow_with_audio(images, audio_path):
    """随机选择图片播放 IMAGE_DURATION，添加淡入淡出动画，与音频时长匹配"""
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    num_images_needed = int(duration // IMAGE_DURATION) + 1

    img_clips = []
    for _ in range(num_images_needed):
        img_path = random.choice(images)
        clip = ImageClip(img_path).set_duration(IMAGE_DURATION).resize(height=VIDEO_SIZE[1])
        clip = clip.set_position("center")
        # 添加淡入淡出效果
        clip = clip.crossfadein(FADE_DURATION).crossfadeout(FADE_DURATION)
        img_clips.append(clip)

    slideshow = concatenate_videoclips(img_clips, method="compose")
    slideshow = slideshow.set_duration(duration)
    slideshow = slideshow.set_audio(audio)
    return slideshow

# ========= 主函数封装 =========
def run_video_module(script_file, image_folder="images", audio_folder="audio", output_file="output/final_video.mp4"):
    """生成最终视频"""
    with open(script_file, "r", encoding="utf-8") as f:
        script = json.load(f)

    images = glob(os.path.join(image_folder, "*.jpg"))
    if not images:
        raise RuntimeError("没有找到图片，请检查 images/ 文件夹")

    all_clips = []
    for idx, section in enumerate(script, start=1):
        title = section["title"]
        # 文件名安全处理
        safe_title = "".join(c for c in title if c.isalnum() or c in "_-")
        audio_file = os.path.join(audio_folder, f"{idx}-{safe_title}.wav")

        if not os.path.exists(audio_file):
            print(f"⚠️ 音频缺失: {audio_file}")
            continue

        title_clip = make_title_frame(title)
        slideshow = make_slideshow_with_audio(images, audio_file)

        all_clips.extend([title_clip, slideshow])

    final = concatenate_videoclips(all_clips, method="compose")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    final.write_videofile(output_file, fps=FPS, codec="libx264", audio_codec="aac")

    print(f"视频生成完成: {output_file}")
    return output_file

# ---------------- 测试 ----------------
if __name__ == "__main__":
    SCRIPT_FILE = "text/四羊方尊_script.json"
    run_video_module(SCRIPT_FILE)
