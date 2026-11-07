#!/usr/bin/env python3
"""
NyayaAI — Fetch and Standardize Complete Indian Penal Code, 1860 (All 511 Sections)
"""
import urllib.request
import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ACTS_DIR = ROOT_DIR / "data" / "raw" / "acts"
ACTS_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://raw.githubusercontent.com/civictech-India/Indian-Law-Penal-Code-Json/master/ipc.json"

ROMAN_MAP = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", "5A": "VA", 6: "VI", 7: "VII",
    8: "VIII", 9: "IX", "9A": "IXA", 10: "X", 11: "XI", 12: "XII", 13: "XIII",
    14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX",
    "20A": "XXA", 21: "XXI", 22: "XXII", 23: "XXIII"
}

SEC_304B_TEXT = (
    "(1) Where the death of a woman is caused by any burns or bodily injury or occurs otherwise "
    "than under normal circumstances within seven years of her marriage and it is shown that "
    "soon before her death she was subjected to cruelty or harassment by her husband or any "
    "relative of her husband for, or in connection with, any demand for dowry, such death "
    "shall be called 'dowry death', and such husband or relative shall be deemed to have caused "
    "her death. Explanation.—For the purposes of this sub-section, 'dowry' shall have the same "
    "meaning as in section 2 of the Dowry Prohibition Act, 1961 (28 of 1961). "
    "(2) Whoever commits dowry death shall be punished with imprisonment for a term which shall "
    "not be less than seven years but which may extend to imprisonment for life."
)

def fetch_and_clean_ipc():
    print(f"Fetching complete IPC dataset from {URL}...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw_data = json.loads(resp.read().decode("utf-8"))

    cleaned_sections = []
    seen_sections = set()

    for item in raw_data:
        sec_num = str(item.get("Section", "")).strip()
        sec_title = str(item.get("section_title", "")).strip()
        sec_desc = str(item.get("section_desc", "")).strip()
        chap = item.get("chapter", 1)
        chap_title = str(item.get("chapter_title", "")).title().strip()

        if sec_num == "304B" and not sec_desc:
            sec_desc = SEC_304B_TEXT

        roman_chap = ROMAN_MAP.get(chap, str(chap))

        cleaned_sections.append({
            "section_number": sec_num,
            "section_title": sec_title,
            "chapter": roman_chap,
            "chapter_title": chap_title,
            "section_text": sec_desc,
            "legal_domain": "Criminal Law"
        })
        seen_sections.add(sec_num)

    full_act = {
        "act_id": "ACT_IPC_1860",
        "act_name": "Indian Penal Code, 1860",
        "short_title": "IPC",
        "year": 1860,
        "enactment_date": "1860-10-06",
        "repeal_date": "2024-07-01",
        "jurisdiction": "India",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2263",
        "total_sections": len(cleaned_sections),
        "unique_sections_count": len(seen_sections),
        "sections": cleaned_sections
    }

    out_file = ACTS_DIR / "ipc_1860_full.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_act, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {out_file} with {len(cleaned_sections)} sections ({len(seen_sections)} unique section IDs)!")
    return out_file

if __name__ == "__main__":
    fetch_and_clean_ipc()

