import wikipediaapi
from ddgs import DDGS
import os
import requests
import io
from PIL import Image
import json

# ---------------- Wikipedia 分章节 ----------------
def wiki_search_sections(query, lang="zh"):
    wiki_wiki = wikipediaapi.Wikipedia(
        language=lang,
        user_agent="video-generator/1.0 (https://github.com/780308)"
    )
    page = wiki_wiki.page(query)
    if not page.exists():
        return {}

    sections_dict = {}


    first_paragraph = page.text.split("\n", 1)[0].strip()
    if first_paragraph:
        sections_dict["首段"] = first_paragraph

    def extract_sections(sections):
        result = {}
        for s in sections:
            if s.text.strip():
                result[s.title] = s.text.strip()
            if s.sections:
                result.update(extract_sections(s.sections))
        return result

    sections_dict.update(extract_sections(page.sections))
    return sections_dict

def save_text_sections(query, sections, save_dir="text"):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{query}_sections.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    return file_path


def download_ddgs_images(query, target_num=20, save_dir="images", batch_size=20, max_attempts=20):
    """
    1. 检测图片能否打开
    2. 避免重复下载
    3. 失败自动尝试下一个图片，直到达到目标数量
    """
    os.makedirs(save_dir, exist_ok=True)
    downloaded_files = []
    seen_urls = set()
    attempts = 0

    while len(downloaded_files) < target_num and attempts < max_attempts:
        attempts += 1
        print(f"尝试下载第 {attempts} 批图片...")

        with DDGS() as ddgs:
            candidates = [r["image"] for r in ddgs.images(query, max_results=batch_size)]
        
        for url in candidates:
            if len(downloaded_files) >= target_num:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                # 检查图片是否能打开
                try:
                    img = Image.open(io.BytesIO(resp.content))
                    img.verify()
                except:
                    continue

                # 文件扩展名处理
                ext = os.path.splitext(url)[1].lower().split("?")[0]
                if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
                    ext = ".jpg"

                filename = os.path.join(save_dir, f"{query}_{len(downloaded_files)}{ext}")
                with open(filename, "wb") as f:
                    f.write(resp.content)
                downloaded_files.append(filename)
                print(f"下载成功: {filename}")
            except:
                continue

        if len(downloaded_files) < target_num:
            print(f"当前有效图片数: {len(downloaded_files)}, 继续下一批...")

    if len(downloaded_files) < target_num:
        print(f"最终下载到 {len(downloaded_files)} 张有效图片（目标 {target_num} 张）")
    return downloaded_files


# ---------------- 封装搜索模块 ----------------
def run_search_module(query, lang="zh", num_images=15):
    """
    执行搜索模块：获取 Wikipedia 章节文本并下载图片
    """
    print(f"=== 搜索模块: {query} ===")
    
    # 1. 获取 Wikipedia 分章节文本
    sections = wiki_search_sections(query, lang=lang)
    if not sections:
        raise ValueError(f"Wikipedia 页面未找到: {query}")
    
    # 2. 保存章节文本为 JSON
    json_file = save_text_sections(query, sections)
    print(f"已保存章节 JSON: {json_file}")

    # 3. 下载图片
    images = download_ddgs_images(query, target_num=num_images)
    print(f"下载完成 {len(images)} 张图片")

    return json_file, images

# ---------------- 测试 ----------------
if __name__ == "__main__":
    query = "越王勾践剑"
    json_file, images = run_search_module(query)
    print("搜索模块执行完毕")
