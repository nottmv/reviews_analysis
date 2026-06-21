import json
import time
from pathlib import Path
from pipeline import analyze
from rag import load_reviews, build_index
from judge import judge_answer

def main():
    reviews = load_reviews(["input/zvuk.csv", "input/yandex_music.csv", "input/vk_music.csv"])
    model, embeddings = build_index(reviews)

    gold = json.loads(Path("gold.json").read_text(encoding="utf-8"))
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for item in gold:
        q = item["question"]
        print(f"Q{item['id']}: {q}")
        start = time.time()
        res = analyze(q, reviews, model, embeddings)
        elapsed = time.time() - start

        verdict = res.get("verdict", {})
        has_quotes = len(res.get("sources", [])) > 0
        ok = verdict.get("ok", False)

        # Сохраняем полную информацию в одном объекте
        results.append({
            "id": item["id"],
            "question": q,
            "answer": res.get("answer", ""),
            "sources": res.get("sources", []),
            "verdict": verdict,
            "judge_ok": ok,
            "has_quotes": has_quotes,
            "tools_used": res.get("tools_used", []),
            "steps": res.get("steps", 0),
            "time_sec": round(elapsed, 2)
        })
        print(f"  ok={ok}, quotes={has_quotes}, time={elapsed:.2f}s")

    # Сводка
    passed = sum(1 for r in results if r["judge_ok"])
    grounded = sum(1 for r in results if r["has_quotes"])
    avg_time = round(sum(r["time_sec"] for r in results) / len(results), 2)

    summary = {
        "total_questions": len(gold),
        "judge_pass": passed,
        "judge_pass_rate": round(passed / len(gold), 2),
        "grounded_answers": grounded,
        "avg_time_sec": avg_time
    }

    # Пишем оба файла
    (out_dir / "eval_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\nJudge Pass Rate: {passed}/{len(gold)} ({summary['judge_pass_rate']})")
    print(f"Grounded: {grounded}/{len(gold)}")
    print(f"Avg time: {avg_time}s")
    print(f"Результаты: {out_dir}/eval_results.json, {out_dir}/summary.json")

if __name__ == "__main__":
    main()