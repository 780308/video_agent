# audio_module.py
import os
import json
from TTS.api import TTS

def run_audio_module(script_json_file, output_dir="audio", model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST"):
    """
    根据解说词 JSON 批量生成 TTS 音频
    """
    os.makedirs(output_dir, exist_ok=True)

    # 初始化 TTS
    print(f"=== 初始化 TTS 模型: {model_name} ===")
    tts = TTS(model_name=model_name)

    # 读取解说词 JSON
    with open(script_json_file, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    audio_files = []

    # 按章节生成音频
    for idx, chapter in enumerate(chapters, start=1):
        title = chapter.get("title", "untitled")
        content = chapter.get("content", "")
        
        # 文件名安全处理
        safe_title = "".join(c for c in title if c.isalnum() or c in "_-")
        output_file = os.path.join(output_dir, f"{idx}-{safe_title}.wav")
        
        print(f"生成第 {idx} 章音频: {title}")
        tts.tts_to_file(text=content, file_path=output_file)

        audio_files.append(output_file)

    print("全部章节语音生成完成！")
    return audio_files


# ---------------- 测试 ----------------
if __name__ == "__main__":
    json_file = "text/四羊方尊_script.json"
    audio_files = run_audio_module(json_file)
    print("生成的音频文件列表:")
    for f in audio_files:
        print("-", f)




'''
import json
import os
from TTS.api import TTS

# ---------------- 配置 ----------------
JSON_FILE = "text/越王勾践剑_script.json"  # 存储解说词的 JSON
OUTPUT_DIR = "audio"                       # 输出音频文件夹
MODEL_NAME = "tts_models/zh-CN/baker/tacotron2-DDC-GST"  # 中文 TTS 模型

# ---------------- 准备输出目录 ----------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- 初始化 TTS ----------------
tts = TTS(model_name=MODEL_NAME)

# ---------------- 读取解说词 JSON ----------------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    chapters = json.load(f)

# ---------------- 按章节生成音频 ----------------
for idx, chapter in enumerate(chapters, start=1):
    title = chapter.get("title", "untitled")
    content = chapter.get("content", "")
    
    # 文件名安全处理：去掉非法字符
    safe_title = "".join(c for c in title if c.isalnum() or c in "_-")
    output_file = os.path.join(OUTPUT_DIR, f"{idx}-{safe_title}.wav")
    
    # 生成语音
    print(f"生成第 {idx} 章音频: {title}")
    tts.tts_to_file(text=content, file_path=output_file)

print("全部章节语音生成完成！")
'''