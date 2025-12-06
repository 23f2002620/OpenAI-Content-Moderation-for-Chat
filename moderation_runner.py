#!/usr/bin/env python3
#setx OPENAI_API_KEY
"""
Real-Time Moderation Runner (Python)
- Reads moderation_config.json and test_messages.json
- Calls OpenAI Moderation endpoint
- Applies category thresholds & auto-block logic
- Writes test_results.csv with: message_id,message_text,flagged_categories,confidence_scores,action_taken,response_time_ms
- Implements exponential backoff and per-message delay to avoid 429
"""

import os
import time
import json
import csv
import math
from typing import Dict, Any, List
from openai import OpenAI
from requests import RequestException

CONFIG_PATH = "moderation_config.json"
TEST_PATH = "test_messages.json"
OUTPUT_CSV = "test_results.csv"


with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

with open(TEST_PATH, "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

MODEL = CONFIG.get("model", "omni-moderation-latest")
THRESHOLDS = CONFIG.get("thresholds", {})
ACTIONS = CONFIG.get("actions", {})
AUTO_BLOCK_CONF = CONFIG.get("auto_block_confidence", 0.80)
PER_MESSAGE_DELAY_MS = CONFIG.get("per_message_delay_ms", 200)

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Set OPENAI_API_KEY environment variable before running (or add to code).")

client = OpenAI(api_key=API_KEY)

def interpret_result(result: Dict[str, Any]) -> Dict[str, float]:
    """
    Normalize moderation result into category->score floats.
    The moderation response generally contains:
      result['category_scores'] and result['categories'] (boolean)
    """
    cat_scores = result.get("category_scores") or {}
    if isinstance(cat_scores, dict) and any(isinstance(v, (int, float)) for v in cat_scores.values()):
        return {k: float(v) for k, v in cat_scores.items()}

    bools = result.get("categories") or {}
    if isinstance(bools, dict):
        return {k: (1.0 if v else 0.0) for k, v in bools.items()}

    return {}

def decide_action(scores: Dict[str, float]) -> (str, Dict[str, float]):
    """
    Decide on action: 'allow', 'review', or 'block'
    Returns action and flagged dict of category->score
    """
    flagged = {}
    action = "allow"
    for cat, score in scores.items():
        th = THRESHOLDS.get(cat, 0.8)
        if score >= AUTO_BLOCK_CONF and cat in ACTIONS.get("block", []):
            flagged[cat] = score
            action = "block"
        elif score >= th:
            flagged[cat] = score
            action = "block" if cat in ACTIONS.get("block", []) else "review"
    return action, flagged

def moderate_text_with_retry(text: str, max_retries=5, base_backoff=2.0):
    """
    Call the moderation endpoint with retries and exponential backoff for 429.
    Returns tuple (raw_result_dict, latency_ms) or (None, -1) on persistent failure.
    """
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        start = time.time()
        try:
            resp = client.moderations.create(model=MODEL, input=text)
            latency_ms = (time.time() - start) * 1000.0
            return resp, latency_ms
        except Exception as e:

            msg = str(e)
            if "429" in msg or "RateLimit" in msg or "quota" in msg.lower():
                wait = base_backoff ** attempt
                print(f"[WARN] attempt {attempt} got rate/quota error; sleeping {wait:.1f}s then retrying...")
                time.sleep(wait)
                continue
            else:
                print(f"[ERROR] Non-retryable exception: {e}")
                return None, -1
    print("[ERROR] Max retries reached, giving up on message.")
    return None, -1


with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "message_id", "message_text", "flagged_categories", "confidence_scores", "action_taken", "response_time_ms"
    ])
    writer.writeheader()

    for m in MESSAGES:
        text = m["text"]
        print(f"Moderating id={m['id']}: {text[:70]}...")
        resp, latency = moderate_text_with_retry(text)

        if resp is None:
            writer.writerow({
                "message_id": m["id"],
                "message_text": text,
                "flagged_categories": json.dumps({"error": "failed"}),
                "confidence_scores": "{}",
                "action_taken": "error",
                "response_time_ms": -1
            })
        else:
            try:
                raw_result = resp["results"][0] if isinstance(resp, dict) and "results" in resp else resp.results[0]
            except Exception:
                raw_result = resp

            scores = interpret_result(raw_result)
            action, flagged = decide_action(scores)

            writer.writerow({
                "message_id": m["id"],
                "message_text": text,
                "flagged_categories": json.dumps(flagged, ensure_ascii=False),
                "confidence_scores": json.dumps(scores, ensure_ascii=False),
                "action_taken": action,
                "response_time_ms": round(latency, 2)
            })

        time.sleep(PER_MESSAGE_DELAY_MS / 1000.0)

print("Done. Results written to", OUTPUT_CSV)
