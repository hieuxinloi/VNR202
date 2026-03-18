import argparse
import json
import re
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


@dataclass(frozen=True)
class Choice:
    key: str
    text: str


@dataclass(frozen=True)
class Question:
    id: int
    prompt: str
    choices: list[Choice]
    answer: str


def extract_paragraphs(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)

    paragraphs: list[str] = []
    for p in root.findall(".//w:p", W_NS):
        texts = [t.text for t in p.findall(".//w:t", W_NS) if t.text]
        if not texts:
            continue
        s = "".join(texts)
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            paragraphs.append(s)
    return paragraphs


QUESTION_RE = re.compile(r"^Câu\s*\d+\b", re.IGNORECASE)


def _normalize_line(line: str) -> str:
    line = line.replace("→", " -> ")
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"(Câu\s*\d+)([A-Za-zÀ-ỹ])", r"\1 \2", line)
    return line


def _split_mcq(question_part: str) -> tuple[str, list[Choice]]:
    parts = re.split(r"\s*([A-D])\.\s*", question_part)
    if len(parts) < 3:
        return question_part.strip(), []
    prompt = parts[0].strip()
    choices: list[Choice] = []
    for i in range(1, len(parts) - 1, 2):
        key = parts[i].strip()
        text = parts[i + 1].strip()
        if key and text:
            choices.append(Choice(key=key, text=text))
    return prompt, choices


def _extract_answer(ans_part: str) -> str:
    ans_part = ans_part.strip()
    m = re.search(r"\b([A-D])\b", ans_part, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    if "đúng" in ans_part.lower():
        return "Đ"
    if "sai" in ans_part.lower():
        return "S"
    return ans_part


def parse_questions(paragraphs: list[str]) -> list[Question]:
    questions: list[Question] = []
    q_id = 1
    pending_prompt: str | None = None

    def finalize(question_part: str, ans_part: str) -> None:
        nonlocal q_id
        question_part = re.sub(
            r"^Câu\s*\d+\s*", "", question_part, flags=re.IGNORECASE
        ).strip()
        if not question_part:
            return

        prompt = question_part
        choices: list[Choice] = []

        if "Đúng / Sai" in question_part or question_part.lower().startswith("đúng / sai"):
            prompt = question_part.replace("Đúng / Sai:", "").strip()
            choices = [Choice(key="Đ", text="Đúng"), Choice(key="S", text="Sai")]
        else:
            prompt, choices = _split_mcq(question_part)

        answer = _extract_answer(ans_part)
        questions.append(Question(id=q_id, prompt=prompt, choices=choices, answer=answer))
        q_id += 1

    for raw in paragraphs:
        line = _normalize_line(raw)
        if not line:
            continue

        if line.lower().startswith("phần"):
            continue

        # Answer marker on its own line (e.g. "-> Đồng Khởi")
        if line.strip().startswith("->"):
            if pending_prompt:
                finalize(pending_prompt, line.replace("->", "", 1).strip())
                pending_prompt = None
            continue

        # Inline answer markers
        if "Đáp án:" in line or "->" in line:
            if "Đáp án:" in line:
                question_part, ans_part = line.split("Đáp án:", 1)
            else:
                question_part, ans_part = line.split("->", 1)
            finalize(question_part, ans_part)
            pending_prompt = None
            continue

        # Start of a numbered question block (e.g. "41. Sắp xếp...")
        if re.match(r"^\d+\.\s*", line):
            pending_prompt = re.sub(r"^\d+\.\s*", "", line).strip()
            continue

        # Continuation lines for a pending prompt (letters list, etc.)
        if pending_prompt:
            pending_prompt = f"{pending_prompt} {line}".strip()
            continue

    # Override specific "scramble letters" prompts if present
    scramble_overrides = {
        "Đồng Khởi": "Sắp xếp các chữ cái sau thành một cụm từ có nghĩa: H / G / K / Ồ / Đ / I / N / Ở",
        "Đường Trường Sơn": "Sắp xếp các chữ cái sau thành một cụm từ có nghĩa: Ơ / T / N / Ờ / S / G / Đ / Ư / N / Ờ / R / G / N / Ư",
        "Mặt trận Dân tộc Giải phóng": "Sắp xếp các chữ cái sau thành một cụm từ có nghĩa: N / P / Â / Ộ / M / G / T / I / Ả / Ậ / D / N / Ặ / H / T / G / Ó / T / R / I / C / N",
        "Ấp Bắc": "Sắp xếp các chữ cái sau thành một cụm từ có nghĩa: C / Ấ / B / Ắ / P",
        "Vịnh Bắc Bộ": "Sắp xếp các chữ cái sau thành một cụm từ có nghĩa: B / V / Ộ / Ị / H / Ắ / C / N / B",
    }

    updated: list[Question] = []
    for q in questions:
        if q.answer in scramble_overrides:
            q = Question(
                id=q.id,
                prompt=scramble_overrides[q.answer],
                choices=q.choices,
                answer=q.answer,
            )
        updated.append(q)

    return updated


def questions_to_json_serializable(questions: list[Question]) -> list[dict]:
    out: list[dict] = []
    for q in questions:
        d = asdict(q)
        d["choices"] = [{"key": c.key, "text": c.text} for c in q.choices]
        out.append(d)
    return out


def write_outputs(questions: list[Question], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = questions_to_json_serializable(questions)

    json_path = out_dir / "questions.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    js_path = out_dir / "questions.js"
    js_path.write_text(
        "// Auto-generated. Source: quiz.docx\n"
        "// Edit questions.json or quiz.docx, then re-run tools/convert_quiz_docx.py\n"
        f"window.QUESTION_BANK = {json.dumps(payload, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8",
    )

    return json_path, js_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert quiz.docx into questions.json + questions.js")
    parser.add_argument("docx", type=Path, help="Path to quiz.docx")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Output directory (default: snakes-and-ladders-game/)",
    )
    args = parser.parse_args()

    paragraphs = extract_paragraphs(args.docx)
    questions = parse_questions(paragraphs)
    json_path, js_path = write_outputs(questions, args.out_dir)

    print(f"Parsed {len(questions)} questions")
    print(f"Wrote {json_path}")
    print(f"Wrote {js_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
