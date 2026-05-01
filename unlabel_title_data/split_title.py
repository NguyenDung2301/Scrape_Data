import json
import random

# Read the sampled file
with open(r'C:\\Users\\Admin\\MyProject\\ScrapeData\\title_data\\unlabel_merged_titles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Shuffle the data
random.shuffle(data)

# Split into 4 parts of 255 samples each
part_size = 255
part1 = data[0:part_size]
part2 = data[part_size:part_size*2]
part3 = data[part_size*2:part_size*3]
part4 = data[part_size*3:part_size*4]

# Save the 4 parts to separate files
output_dir = r'C:\\Users\\Admin\\MyProject\\ScrapeData\\title_data'

output_path1 = f'{output_dir}\\unlabel_title.part1.json'
output_path2 = f'{output_dir}\\unlabel_title.part2.json'
output_path3 = f'{output_dir}\\unlabel_title.part3.json'
output_path4 = f'{output_dir}\\unlabel_title.part4.json'

with open(output_path1, 'w', encoding='utf-8') as f:
    json.dump(part1, f, ensure_ascii=False, indent=2)

with open(output_path2, 'w', encoding='utf-8') as f:
    json.dump(part2, f, ensure_ascii=False, indent=2)

with open(output_path3, 'w', encoding='utf-8') as f:
    json.dump(part3, f, ensure_ascii=False, indent=2)

with open(output_path4, 'w', encoding='utf-8') as f:
    json.dump(part4, f, ensure_ascii=False, indent=2)

print(f"Part 1: {len(part1)} samples -> {output_path1}")
print(f"Part 2: {len(part2)} samples -> {output_path2}")
print(f"Part 3: {len(part3)} samples -> {output_path3}")
print(f"Part 4: {len(part4)} samples -> {output_path4}")    
print(f"\nTổng: {len(part1) + len(part2) + len(part3) + len(part4)} samples")
