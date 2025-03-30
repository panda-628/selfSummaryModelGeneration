import json
import re
from sentence_transformers import SentenceTransformer, util
import torch

# 初始化语义模型（首次运行需要下载约100MB模型文件）
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def normalize_relationship(relationship):
    """规范化关系描述（保持原逻辑）"""
    pattern = r'(\w+)\s*["\']([^"\']*)["\']\s*(--|-->)\s*["\']([^"\']*)["\']\s*(\w+)'
    match = re.match(pattern, relationship)
    return (match.group(1), match.group(5)) if match else None

def semantic_compare(items_a, items_b, threshold=0.75):
    """执行语义感知的集合比较"""
    # 去重处理
    unique_a = list(set(items_a))
    unique_b = list(set(items_b))
    
    # 边界情况处理
    if not unique_a and not unique_b: return [], []
    if not unique_a: return [], unique_b
    if not unique_b: return unique_a, []
    
    # 批量编码提高效率
    embeddings = model.encode(unique_a + unique_b, convert_to_tensor=True)
    emb_a = embeddings[:len(unique_a)]
    emb_b = embeddings[len(unique_a):]
    
    # 计算相似度矩阵
    similarity_matrix = util.pytorch_cos_sim(emb_a, emb_b)
    
    # 找出新增项（生成中存在但Oracle无相似）
    add = [
        item for i, item in enumerate(unique_a)
        if torch.max(similarity_matrix[i]) < threshold
    ]
    
    # 找出缺失项（Oracle中存在但生成无相似）
    miss = [
        item for j, item in enumerate(unique_b)
        if torch.max(similarity_matrix[:, j]) < threshold
    ]
    
    return add, miss

def compare_files(generated_data, oracle_data, similarity_threshold=0.75):
    """改进后的比较函数"""
    result = {
        'enumeration': {'add': [], 'miss': []},
        'class': {'add': [], 'miss': []},
        'relationships': {'add': [], 'miss': []}
    }
    
    # 语义比较枚举和类
    for key in ['enumeration', 'class']:
        gen_items = generated_data.get(key, [])
        ora_items = oracle_data.get(key, [])
        
        add, miss = semantic_compare(gen_items, ora_items, similarity_threshold)
        result[key]['add'] = add
        result[key]['miss'] = miss
    
    # 关系比较保持原逻辑
    # 处理关系
    generated_relationships = {normalize_relationship(rel) for rel in generated_data.get('relationships', [])}
    print("正则化后的生成的关系：", generated_relationships)
    oracle_relationships = {normalize_relationship(rel) for rel in oracle_data.get('relationships', [])}
    print("正则化后的oracle关系：", oracle_relationships)

    # 过滤掉 None 值
    generated_relationships = {frozenset(rel) for rel in generated_relationships if rel is not None}
    oracle_relationships = {frozenset(rel) for rel in oracle_relationships if rel is not None}

    result['relationships']['add'] = [
        rel for rel in generated_data.get('relationships', [])
        if normalize_relationship(rel) and frozenset(normalize_relationship(rel)) not in oracle_relationships
    ]
    result['relationships']['miss'] = [
        rel for rel in oracle_data.get('relationships', [])
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
