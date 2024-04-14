import os
from opencc import OpenCC

def merge_md_files(directory, output_file):
    cc = OpenCC('t2s')  # 繁体转简体

    # 生成文件名列表（从 scp-001.md 到 scp-7999.md）
    expected_files = [f"scp-{i:03}.md" for i in range(1, 8000)]
    
    # 打开输出文件准备写入，使用缓冲区
    with open(output_file, 'w', encoding='utf-8', buffering=1) as outfile:
        for filename in expected_files:
            filepath = os.path.join(directory, filename)
            # 检查文件是否存在
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        for line in infile:
                            # 对每行进行繁简转换，逐行写入减少内存压力
                            simplified_line = cc.convert(line)
                            outfile.write(simplified_line)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

# 调用函数，指定目录和输出文件名
merge_md_files('scp_md', 'all.md')
