"""补充项目中文简介：人工翻译优先，缺失时使用百度通用文本翻译 API。"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_FILE = PROJECT_ROOT / "data" / "projects.json"
LOCALES_FILE = PROJECT_ROOT / "data" / "project_locales.json"
USAGE_FILE = PROJECT_ROOT / "data" / "baidu_translation_usage.json"
BAIDU_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"
MONTHLY_CHAR_LIMIT = 900_000
CHINESE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(path)


def _has_chinese(value: str) -> bool:
    return bool(CHINESE_RE.search(value))


def _translate(text: str, app_id: str, secret_key: str) -> str | None:
    salt = str(random.randint(10000, 99999))
    sign = hashlib.md5(
        f"{app_id}{text}{salt}{secret_key}".encode("utf-8")
    ).hexdigest()
    response = requests.post(
        BAIDU_URL,
        data={
            "q": text,
            "from": "auto",
            "to": "zh",
            "appid": app_id,
            "salt": salt,
            "sign": sign,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error_code"):
        raise RuntimeError(
            f"百度翻译错误 {payload['error_code']}: {payload.get('error_msg', '')}"
        )
    translations = payload.get("trans_result") or []
    translated = translations[0].get("dst") if translations else ""
    return str(translated).strip() or None


def main() -> int:
    projects = _read_json(PROJECTS_FILE, [])
    locales = _read_json(LOCALES_FILE, {})
    if not isinstance(projects, list) or not isinstance(locales, dict):
        raise ValueError("项目数据或中文配置格式不正确")

    app_id = os.getenv("BAIDU_APP_ID", "").strip()
    secret_key = os.getenv("BAIDU_SECRET_KEY", "").strip()
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    usage = _read_json(USAGE_FILE, {})
    if not isinstance(usage, dict) or usage.get("month") != month:
        usage = {"month": month, "characters": 0}
    used_characters = int(usage.get("characters", 0) or 0)

    locales_changed = False
    translated_count = 0
    chinese_source_count = 0
    skipped_count = 0

    for project in projects:
        if not isinstance(project, dict):
            continue
        key = str(project.get("full_name") or project.get("name") or "").strip()
        source_description = str(project.get("description") or "").strip()
        if not key or not source_description:
            continue

        entry = locales.get(key)
        if not isinstance(entry, dict):
            entry = {}
            locales[key] = entry

        # 人工维护的中文简介永远优先，不被自动翻译覆盖。
        if str(entry.get("description") or "").strip():
            continue

        # GitHub 返回的简介本身已经是中文时，直接保存，不消耗翻译额度。
        if _has_chinese(source_description):
            entry["description"] = source_description
            chinese_source_count += 1
            locales_changed = True
            continue

        if not app_id or not secret_key:
            skipped_count += 1
            continue

        source_characters = len(source_description)
        if used_characters + source_characters > MONTHLY_CHAR_LIMIT:
            print(f"已达到本月安全额度上限，停止翻译：{key}")
            skipped_count += 1
            continue

        try:
            translated = _translate(source_description, app_id, secret_key)
        except (requests.RequestException, ValueError, RuntimeError, KeyError, IndexError) as exc:
            print(f"百度翻译失败，保留英文简介：{key} - {exc}")
            skipped_count += 1
            continue

        if translated:
            entry["description"] = translated
            used_characters += source_characters
            translated_count += 1
            locales_changed = True

    if locales_changed:
        _write_json(LOCALES_FILE, locales)
    if used_characters or USAGE_FILE.exists():
        _write_json(USAGE_FILE, {"month": month, "characters": used_characters})

    print(
        f"中文简介处理完成：人工翻译优先，"
        f"GitHub 自带中文 {chinese_source_count} 条，"
        f"百度翻译 {translated_count} 条，未处理 {skipped_count} 条；"
        f"本月已计费字符 {used_characters}/{MONTHLY_CHAR_LIMIT}。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
