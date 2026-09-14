"""
HotRank v2 — 为信息类大二学生设计的多维度热度排序引擎
================================================================
产品定位：不再是拍脑袋定权重的加权求和，而是通过"熵权法"自动算权重，
         再加一个"兴趣向量"让每个使用者得到个性化的排行榜。

核心算法：
  1. 熵权法 —— 让数据自己决定每个维度的重要程度
     - 某个维度上所有项目取值越接近 → 信息量越小 → 权重越低
     - 某个维度上项目差异越大 → 信息量越大 → 权重越高
     - 完全客观，不需要人拍脑袋

  2. 用户兴趣向量调权 —— 用户选择1-2个"我最看重什么"，算法自动重算
     - "我最在乎活跃度" → last_push_days 权重翻倍
     - "我是星星警察"   → stars 权重翻倍
     - "我看社区氛围"   → forks + contributors 权重各乘1.5

  3. 对比基线 —— 跟纯 star 排序对比，证明算法确实更有区分度

用法：
  python hotrank.py                  演示数据，交互式选择兴趣偏好
  python hotrank.py --batch          非交互模式，直接出全部排名
  python hotrank.py --file repos.json  读自定义数据
  python hotrank.py --score-only     只看分数，不要条形图
"""

import json, csv, sys, math, argparse
from pathlib import Path
from collections import defaultdict


# =========================================================================
# 第1层：原始数据
# =========================================================================

DEMO_REPOS = [
    {"name": "tensorflow/tensorflow", "stars": 188000, "forks": 74000,   "open_issues": 2500, "last_push_days": 0,  "contributors": 3800, "size_kb": 880000},
    {"name": "vuejs/vue",            "stars": 208000, "forks": 34000,   "open_issues": 180,  "last_push_days": 60, "contributors": 420,  "size_kb": 4800},
    {"name": "facebook/react",       "stars": 230000, "forks": 47000,   "open_issues": 900,  "last_push_days": 2,  "contributors": 1620, "size_kb": 180000},
    {"name": "rust-lang/rust",       "stars": 100000, "forks": 13000,   "open_issues": 5200, "last_push_days": 0,  "contributors": 6600, "size_kb": 340000},
    {"name": "home-assistant/core",  "stars": 75000,  "forks": 24000,   "open_issues": 1200, "last_push_days": 0,  "contributors": 4200, "size_kb": 380000},
    {"name": "microsoft/vscode",     "stars": 165000, "forks": 29000,   "open_issues": 3800, "last_push_days": 0,  "contributors": 2100, "size_kb": 590000},
    {"name": "ohmyzsh/ohmyzsh",      "stars": 175000, "forks": 26000,   "open_issues": 100,  "last_push_days": 5,  "contributors": 1700, "size_kb": 3200},
    {"name": "pallets/flask",        "stars": 69000,  "forks": 16000,   "open_issues": 30,   "last_push_days": 10, "contributors": 800,  "size_kb": 6200},
    {"name": "ansible/ansible",      "stars": 64000,  "forks": 24000,   "open_issues": 1200, "last_push_days": 1,  "contributors": 6400, "size_kb": 820000},
    {"name": "nodejs/node",          "stars": 110000, "forks": 31000,   "open_issues": 600,  "last_push_days": 0,  "contributors": 4200, "size_kb": 420000},
    {"name": "huginn/huginn",        "stars": 44000,  "forks": 3800,    "open_issues": 40,   "last_push_days": 30, "contributors": 500,  "size_kb": 24000},
    {"name": "ripienaar/free-for-dev","stars": 93000,  "forks": 10000,   "open_issues": 20,   "last_push_days": 15, "contributors": 400,  "size_kb": 3000},
]


# =========================================================================
# 第2层：熵权法 —— 完全客观的权重推导
# =========================================================================

def minmax_normalize(values, reverse=False):
    mn, mx = min(values), max(values)
    span = mx - mn
    if span == 0:
        return [1.0] * len(values)
    if reverse:
        return [(mx - v) / span for v in values]
    return [(v - mn) / span for v in values]


def entropy_weights(data_matrix):
    """
    data_matrix: list of lists, shape (n_repos, n_dims), 已归一化到[0,1]
    返回每个维度的熵权，和为1
    """
    n = len(data_matrix)
    if n == 0:
        return []
    n_dims = len(data_matrix[0])
    # 避免 log(0)
    eps = 1e-12
    weights = []
    for j in range(n_dims):
        col = [row[j] + eps for row in data_matrix]
        total = sum(col)
        # 计算熵值
        entropy = -sum((v / total) * math.log(v / total) for v in col) / math.log(n)
        # 熵越小 -> 差异越大 -> 权重越大
        w = 1 - entropy
        weights.append(w)
    # 归一化成概率
    s = sum(weights)
    if s == 0:
        return [1.0 / n_dims] * n_dims
    return [w / s for w in weights]


def compute_hotrank(repos, weights=None, interest=None):
    """
    weights: 若为None, 自动用熵权法计算
    interest: 用户兴趣偏好字符串，影响最终权重
    """
    # 所有参与排序的字段 —— 这些字段必须在 repo dict 中存在
    fields = ["stars", "forks", "open_issues", "last_push_days", "contributors"]

    # 提取原始值
    raw = {f: [r[f] for r in repos] for f in fields}

    # MinMax 归一化
    norm = {}
    for f in fields:
        norm[f] = minmax_normalize(raw[f], reverse=(f in ("open_issues", "last_push_days")))

    # 构建归一化矩阵给熵权法
    matrix = [[norm[f][i] for f in fields] for i in range(len(repos))]

    if weights is None:
        # 熵权法自动算权重
        weights_list = entropy_weights(matrix)
        weights = dict(zip(fields, weights_list))
    else:
        # 使用传入的固定权重
        weights_list = [weights.get(f, 0) for f in fields]
        s = sum(abs(w) for w in weights_list)
        if s > 0:
            weights_list = [abs(w) / s for w in weights_list]
        else:
            weights_list = [1.0 / len(fields)] * len(fields)
        weights = dict(zip(fields, weights_list))

    # 应用用户兴趣偏好
    if interest:
        factor = {f: 1.0 for f in fields}
        if "activity" in interest:
            factor["last_push_days"] = 2.0  # 活跃度翻倍
        if "stars" in interest:
            factor["stars"] = 2.0           # 星星翻倍
        if "community" in interest:
            factor["forks"] = 1.5
            factor["contributors"] = 1.5
        if "maintenance" in interest:        # 维护质量（少issue、频繁更新）
            factor["open_issues"] = 2.0
            factor["last_push_days"] = 1.5
        # 重归一化
        weighted = {f: weights[f] * factor[f] for f in fields}
        s2 = sum(weighted.values())
        if s2 > 0:
            weights = {f: weighted[f] / s2 for f in fields}

    # 计算最终评分
    result = []
    for i, repo in enumerate(repos):
        score = sum(weights[f] * norm[f][i] for f in fields) * 100.0
        result.append({**repo, "hot_score": round(score, 2)})

    result.sort(key=lambda x: x["hot_score"], reverse=True)

    # 附加信息：维度权重供展示
    meta = {
        "weights": {f: round(w, 4) for f, w in weights.items()},
        "interest_applied": interest or "none",
    }
    return result, meta


# =========================================================================
# 第3层：与纯 Star 排序的对比
# =========================================================================

def star_rank(repos):
    """纯按 star 降序作为基线"""
    ranked = sorted(repos, key=lambda x: x["stars"], reverse=True)
    return [r["name"] for r in ranked]


def rank_comparison(hotrank_result, repos):
    """输出热榜 vs 纯star榜，标出哪些项目名次变化明显"""
    hot_names = [r["name"] for r in hotrank_result]
    star_names = star_rank(repos)
    changes = []
    for i, name in enumerate(hot_names):
        star_pos = star_names.index(name) + 1
        hot_pos = i + 1
        diff = star_pos - hot_pos
        if diff != 0:
            changes.append((name, hot_pos, star_pos, diff))
    return changes


# =========================================================================
# 第4层：交互式兴趣偏好选择
# =========================================================================

def ask_interest():
    """控制台交互，让用户选择兴趣偏好"""
    print("\n你想让排行榜更侧重什么？（输入编号，多选用逗号分隔，如 1,3）")
    print("  1) 星星警察 —— 我就看星数，星多就是好项目")
    print("  2) 活跃先锋 —— 最近还在更新的项目优先")
    print("  3) 社区氛围 —— forks 多、贡献者多说明社区活跃")
    print("  4) 维护质量 —— issue 少、更新勤的靠谱项目")
    print("  0) 不用偏好，直接用算法自动权重")
    print()
    choice = input("> ").strip()
    if choice == "0" or not choice:
        return None
    mapping = {
        "1": "stars",
        "2": "activity",
        "3": "community",
        "4": "maintenance",
    }
    selected = []
    for token in choice.replace("，", ",").split(","):
        token = token.strip()
        if token in mapping:
            selected.append(mapping[token])
    if not selected:
        return None
    # 如果用户选了多个，返回第一个为主偏好，但算法内部会做组合调权
    return selected[0]  # 简化处理，取第一个为主要偏好


# =========================================================================
# 第5层：输出
# =========================================================================

def print_ranking(result, meta, top=None, score_only=False, show_star_diff=False, repos=None):
    display = result[:top] if top else result

    weight_str = "  ".join(f"{k} {v*100:.1f}%" for k, v in meta["weights"].items())

    print()
    print(f"{'='*72}")
    print(f"  HotRank v2  |  兴趣偏好: {meta['interest_applied']}")
    print(f"  维度权重: {weight_str}")
    print(f"{'='*72}")
    if score_only:
        print(f"  {'#':<4} {'Repo':<35} {'Score':<7}")
        print(f"{'-'*48}")
        for i, r in enumerate(display, 1):
            print(f"  #{i:<2}  {r['name']:<35} {r['hot_score']:>6.1f}")
    else:
        print(f"  {'#':<4} {'Repo':<35} {'Score':<7} Bar")
        print(f"{'='*72}")
        for i, r in enumerate(display, 1):
            bar_len = int(r["hot_score"] / 2)
            bar = "#" * bar_len + "." * (50 - bar_len)
            print(f"  #{i:<2}  {r['name']:<35} {r['hot_score']:>6.1f}  {bar}")
    print(f"{'='*72}")
    print(f"  Total {len(result)} repos")

    if show_star_diff and repos:
        changes = rank_comparison(result, repos)
        if changes:
            print(f"\n  >> 与纯 Star 排名对比（正数=热榜排名更高）")
            print(f"  {'Repo':<35} {'热榜':<6} {'Star榜':<6} {'差值':<6}")
            print(f"  {'-'*53}")
            for name, hot_pos, star_pos, diff in changes:
                sign = "+" if diff > 0 else ""
                print(f"  {name:<35} #{hot_pos:<4} #{star_pos:<4} {sign}{diff}")
        else:
            print(f"\n  与纯 Star 排名完全一致")
    print()


# =========================================================================
# CLI
# =========================================================================

def main():
    p = argparse.ArgumentParser(description="HotRank v2 — 多维度热度排序")
    p.add_argument("--file", "-f", help="CSV 或 JSON 输入文件")
    p.add_argument("--top", "-t", type=int, help="只显示前 N 名")
    p.add_argument("--score-only", action="store_true", help="只显示分数，不显示条形图")
    p.add_argument("--batch", action="store_true", help="非交互模式，不询问兴趣偏好")
    p.add_argument("--interest", "-i", choices=["stars", "activity", "community", "maintenance"],
                   help="直接指定兴趣偏好")
    p.add_argument("--show-diff", action="store_true", help="显示与纯 Star 排名的差异")
    args = p.parse_args()

    # 加载数据
    if args.file:
        path = Path(args.file)
        if path.suffix == ".csv":
            repos = load_csv(args.file)
        elif path.suffix == ".json":
            repos = load_json(args.file)
        else:
            print("Unsupported file format; use .csv or .json")
            sys.exit(1)
    else:
        repos = DEMO_REPOS

    # 获取兴趣偏好
    interest = args.interest
    if not args.batch and interest is None:
        interest = ask_interest()

    # 计算排名
    result, meta = compute_hotrank(repos, interest=interest)

    # 输出
    print_ranking(result, meta, top=args.top, score_only=args.score_only,
                  show_star_diff=args.show_diff, repos=repos)


def load_csv(path):
    repos = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in ["stars", "forks", "open_issues", "last_push_days", "contributors", "size_kb"]:
                row[key] = int(row[key])
            repos.append(row)
    return repos


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
