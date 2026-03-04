from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime


def _safe_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_artifacts(page, test_name: str, out_dir: str = "artifacts") -> dict:
    """
    Сохраняет screenshot + html для текущей страницы.
    Возвращает пути к файлам.
    """
    out = ensure_dir(out_dir)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = _safe_name(f"{test_name}_{ts}")

    png_path = out / f"{base}.png"
    html_path = out / f"{base}.html"
    meta_path = out / f"{base}.txt"

    # screenshot
    try:
        page.screenshot(path=str(png_path), full_page=True)
    except Exception as exc:
        print(f"⚠️ Не удалось сохранить screenshot: {exc}")

    # html
    try:
        html_path.write_text(page.content(), encoding="utf-8")
    except Exception as exc:
        print(f"⚠️ Не удалось сохранить screenshot: {exc}")

    # url/meta
    try:
        meta_path.write_text(f"URL: {page.url}\n", encoding="utf-8")
    except Exception as exc:
        print(f"⚠️ Не удалось сохранить screenshot: {exc}")

    # ✅ attach в Allure (если установлен)
    try:
        import allure  # type: ignore

        if png_path.exists():
            allure.attach.file(
                str(png_path),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        if html_path.exists():
            allure.attach.file(
                str(html_path),
                name="page.html",
                attachment_type=allure.attachment_type.HTML,
            )

        if meta_path.exists():
            allure.attach.file(
                str(meta_path),
                name="meta.txt",
                attachment_type=allure.attachment_type.TEXT,
            )

    except Exception as exc:
        print(f"⚠️ Не удалось сохранить screenshot: {exc}")

    return {
        "screenshot": str(png_path),
        "html": str(html_path),
        "meta": str(meta_path),
    }