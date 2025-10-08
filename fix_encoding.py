import json


encodings = ["utf-8"]

for encoding in encodings:
    try:
        with open('all_data.json', 'r', encoding=encoding) as f:
            data = json.load(f)
        print(f'Success with encoding: {encoding}')
        
        with open('all_data.json', 'w', encoding='utf-8') as f:
            data = json.dump(data, f, ensure_ascii=False, indent=2)
        break
        
    except UnicodeDecodeError:
        continue
    except json.JSONDecodeError as e:
        print(f"JSON error with, {encoding}: {e}")