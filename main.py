import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

error=open ("error.txt","w", encoding="UTF-8")


# 确保scp_md文件夹存在
if not os.path.exists('scp_md'):
    os.makedirs('scp_md')

def scrape_scp_page(url):
    content = None
    img_url = None
    img_introduce = None
    title = None
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.replace(' - SCP基金会', '').strip()
        excluded_texts = ["檔案名稱", "圖像名稱", "圖像作者", "圖像授權協議", "連結", "參考資料", "請在引用該頁面時", "1234", "網站資訊查詢", "翻譯專區", "綜合創作", "SCP檔案", "網站连结", "**Content:**"]
        caption_divs = soup.select('div.scp-image-caption')
        excluded_paragraphs = set()
        for div in caption_divs:
            excluded_paragraphs.update(div.find_all('p'))
        strong_paragraphs = [
            p for p in soup.find_all('p')
            if not p.find('a') and all(excluded_text not in p.text for excluded_text in excluded_texts) and p not in excluded_paragraphs
        ]
        content = '\n\n'.join(p.text for p in strong_paragraphs)
        img_blocks = soup.select('div.scp-image-block.block-right')
        if img_blocks:
            img_block = img_blocks[0]
            img_element = img_block.find('img')
            img_url = img_element['src'] if img_element else None
            img_caption_div = img_block.find('div', class_='scp-image-caption')
            if img_caption_div:
                img_introduce = img_caption_div.text.strip()
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")
    return {'title': title, 'img_url': img_url, 'img_introduce': img_introduce, 'content': content}

def process_url(url):
    try:
        result = scrape_scp_page(url)
        scp_number = url.split('/')[-1]
        file_path = f"scp_md/{scp_number}.md"
        full_content = (f"# {result['title']}\n\n" if result['title'] else "") + \
                       (f"![Image]({result['img_url']})\n\n" if result['img_url'] else "") + \
                       (f"**图片介绍：** {result['img_introduce']}\n\n" if result['img_introduce'] else "") + \
                       (f"{result['content']}\n\n" if result['content'] else "")
        if len(full_content) < 159:
            raise ValueError(f"Content length for {url} is less than 159 characters.")
        elif "詢問別人" not in full_content:
            with open(file_path, "w", encoding="UTF-8") as file:
                file.write(full_content)
    except Exception as e:
        error.write(f"Error in {url}: {str(e)}")
        return f"Error in {url}: {str(e)}"  # 这里确保错误信息格式正确

def main():
    urls = [f"http://scp-zh-tr.wikidot.com/scp-{str(i).zfill(3)}" for i in range(1, 8000)]
    with ThreadPoolExecutor(max_workers=10) as executor, open("error.log", "w", encoding="UTF-8") as error_log:
        futures = {executor.submit(process_url, url): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            if result and "Error" in result:
                error_log.write(result + "\n")
                error_log.flush()  # 使用flush确保即时写入
                print(result)  # 输出错误信息到控制台
            else:
                print(f"Processed {futures[future]} successfully.")

if __name__ == "__main__":
    main()

