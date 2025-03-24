import json
import re

def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def normalize_relationship(relationship):
    # 提取关系中的主体并返回一个标准化的元组，确保顺序不影响比较
    pattern = r'(\w+)\s*["\']?\d*\.{0,1}\d*["\']?\s*(--|-->)\s*["\']?\d*\.{0,1}\d*["\']?\s*(\w+)'
    match = re.match(pattern, relationship)
    if match:
        return (match.group(1), match.group(3))  # 返回主体，确保顺序一致
    return None

def compare_files(generated_data, oracle_data):
    result = {
        'enumeration': {'add': [], 'miss': []},
        'class': {'add': [], 'miss': []},
        'relationships': {'add': [], 'miss': []}
    }

    # 比较 enumeration 和 class
    for key in result.keys():
        if key != 'relationships':
            generated_set = set(generated_data.get(key, []))
            oracle_set = set(oracle_data.get(key, []))

            result[key]['add'] = list(generated_set - oracle_set)
            result[key]['miss'] = list(oracle_set - generated_set)
        else:
            # 处理关系
            generated_relationships = {normalize_relationship(rel) for rel in generated_data.get(key, [])}
            print("正则化后的生成的关系：", generated_relationships)
            oracle_relationships = {normalize_relationship(rel) for rel in oracle_data.get(key, [])}
            print("正则化后的oracle关系：", oracle_relationships)

            # 过滤掉 None 值
            generated_relationships = {frozenset(rel) for rel in generated_relationships if rel is not None}
            oracle_relationships = {frozenset(rel) for rel in oracle_relationships if rel is not None}

            result[key]['add'] = [
                rel for rel in generated_data.get(key, [])
                if normalize_relationship(rel) and frozenset(normalize_relationship(rel)) not in oracle_relationships
            ]
            result[key]['miss'] = [
                rel for rel in oracle_data.get(key, [])
                if normalize_relationship(rel) and frozenset(normalize_relationship(rel)) not in generated_relationships
            ]

    return result

def get_changes_summary(result):
    total_insertions = 0
    total_deletions = 0
    summary = []

    for category, data in result.items():
        total_insertions += len(data['add'])
        total_deletions += len(data['miss'])

    summary.append(f"{len(result)} categories changed, {total_insertions} insertions(+), {total_deletions} deletions(-)")

    for category, data in result.items():
        summary.append(f"- **{category}**: {len(data['add'])} insertions(+), {len(data['miss'])} deletions(-)")
        if data['add']:
            summary.append("  added: " + ', '.join(data['add']))
        else:
            summary.append("  added: []")
        if data['miss']:
            summary.append("  absent: " + ', '.join(data['miss']))

    return '\n'.join(summary)

def main(generated_file_path, oracle_file_path):
    generated_data = load_file(generated_file_path)
    oracle_data = load_file(oracle_file_path)

    comparison_result = compare_files(generated_data, oracle_data)
    summary = get_changes_summary(comparison_result)
    
    print(json.dumps(comparison_result, indent=4, ensure_ascii=False))

    return summary

if __name__ == '__main__':
    generated_file_path = 'path/to/generated_file.json'
    oracle_file_path = 'LBTKoracle.json'
    main(generated_file_path, oracle_file_path)