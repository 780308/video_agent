# -*- coding: utf-8 -*-
import json
import re
import ollama
import os

def generate_script_from_json(json_file, model_name="qwen2.5:3b"):
    # 读取检索文本
    with open(json_file, "r", encoding="utf-8") as f:
        sections = json.load(f)

    # 整合成 prompt

    prompt = "你是一个博物馆解说员，你需要根据后面提供的文本生成一段中文解说词，要求如下：1. 必须划分章节，每章必须有标题和内容。一种可能的章节划分方式为：外观、背景历史、相关事件等。2. 每个章节标题使用 **标题** 格式标注，例如：**外观** 3. 第一个章节固定为 **开场白**，示例：我是AI文物讲解员小明，接下来向您介绍…… 4. 每章内容必须完整自然，保持完整句子，不要在中途截断或遗漏信息，每章内容尽量详尽，适当加入细节和生动描述。5. 禁止把文本中提到的图片、参考文献、外部链接等网页内容写入解说词。6. 禁止使用阿拉伯数字和小数点，例如禁止写 20 世纪，应写成 二十世纪；禁止写 54.5，应写成 五十四点五。7. 禁止写“参见”“参考其他词条”等提示语。8. 语言要求逻辑清晰，流畅自然，适合口语化朗读。请根据以下文本生成解说词：\n\n"
    

    for title, text in sections.items():
        prompt += f"【{title}】{text}\n\n"

    # 调用 Ollama 本地模型
    response = ollama.generate(model=model_name, prompt=prompt)

    if hasattr(response, "response"):
        script_text = response.response
    else:
        # 兼容老版本
        results = response.get("results", [])
        script_text = "\n".join([r.get("content", "") for r in results])

        
    pattern = re.compile(r"(?:【|[*]{2})(.*?)(?:】|[*]{2})\s*([\s\S]*?)(?=(?:【|[*]{2}|$))")
    matches = pattern.findall(script_text)

    script_list = []
    for title, content in matches:
        script_list.append({
            "title": title.strip(),
            "content": content.strip()
        })

    return script_list

def save_script_list(script_list, save_file):
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(script_list, f, ensure_ascii=False, indent=2)
    print(f"解说词已保存到 {save_file}")


def run_script_module(json_file, output_file=None, model_name="qwen2.5:3b"):
    """
    执行 script 模块：根据搜索模块生成的原始 JSON，生成分章节解说词并保存
    """
    print(f"=== script 模块: 生成解说词 ===")
    
    # 1. 生成解说词
    script_list = generate_script_from_json(json_file, model_name=model_name)
    
    # 2. 保存解说词 JSON
    if output_file is None:
        base_name = os.path.basename(json_file).replace("_sections.json", "_script.json")
        output_file = os.path.join(os.path.dirname(json_file), base_name)
    save_script_list(script_list, output_file)

    return script_list, output_file


# ---------------- 测试 ----------------
if __name__ == "__main__":
    json_file = "text/越王勾践剑_sections.json"
    script_list, save_file = run_script_module(json_file)
    print("script 模块执行完毕")

