from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Set, Tuple


BASE = Path(__file__).resolve().parents[1] / "config" / "gcp"
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass
class CategoryResult:
    name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


def _load_json(name: str) -> dict:
    path = BASE / name
    if not path.is_file():
        raise RuntimeError(f"GCP validation missing required file: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GCP validation failed to parse {path}: {exc}") from exc


def _option_labels(question: Mapping[str, object]) -> Set[str]:
    """
    Return the set of valid answer labels for a question.
    Supports options declared as strings or {label, value}.
    """
    options = question.get("options", [])
    labels: Set[str] = set()
    for opt in options if isinstance(options, list) else []:
        if isinstance(opt, str):
            label = opt.strip()
        elif isinstance(opt, Mapping):
            label = str(opt.get("label", "")).strip()
        else:
            continue
        if label:
            labels.add(label)
    return labels


def _matrix_combinations(
    question: Mapping[str, object], base_options: Iterable[str]
) -> Set[str]:
    combos: Set[str] = set()
    items = question.get("items", [])
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, Mapping):
            continue
        label = str(item.get("label", "")).strip()
        if not label:
            continue
        for opt in base_options:
            combos.add(f"{label} — {opt}")
    return combos


def _collect_questions(
    schema: dict, schema_res: CategoryResult
) -> Dict[str, Mapping[str, object]]:
    questions: Dict[str, Mapping[str, object]] = {}
    seen_ids: Set[str] = set()
    for section in schema.get("sections", []):
        for question in section.get("questions", []):
            if not isinstance(question, Mapping):
                schema_res.error(
                    f"section '{section.get('id', '<unknown>')}' contains non-object question"
                )
                continue
            qid = question.get("id")
            if not qid:
                schema_res.error(
                    f"section '{section.get('id', '<unknown>')}' contains question without id"
                )
                continue
            if qid in seen_ids:
                schema_res.error(f"duplicate question id '{qid}'")
            seen_ids.add(qid)
            questions[qid] = question
            qtype = question.get("type")
            if qtype in {"single", "multi", "matrix"}:
                opts = _option_labels(question)
                if not opts:
                    schema_res.error(f"question '{qid}' ({qtype}) has no options")
                for opt in opts:
                    if not opt:
                        schema_res.error(
                            f"question '{qid}' has option with empty label"
                        )
    return questions


def _collect_flags(scoring_rows: List[Mapping[str, object]]) -> Set[str]:
    flags: Set[str] = set()
    for row in scoring_rows:
        raw = str(row.get("FlagsEmitted", "") or "").strip()
        if not raw:
            continue
        for token in re.split(r"[,\s;]+", raw):
            token = token.strip()
            if token:
                flags.add(token)
    return flags


def _validate_schema_and_scoring(
    schema: dict,
    scoring_rows: List[Mapping[str, object]],
    domains: Set[str],
    schema_res: CategoryResult,
    scoring_res: CategoryResult,
    domain_res: CategoryResult,
) -> Tuple[Dict[str, Mapping[str, object]], Dict[str, Set[str]]]:
    questions = _collect_questions(schema, schema_res)
    valid_options: Dict[str, Set[str]] = {}
    for qid, question in questions.items():
        base_opts = _option_labels(question)
        combos = set()
        if question.get("type") == "matrix":
            combos = _matrix_combinations(question, base_opts)
        valid_options[qid] = base_opts | combos

    used_domains: Set[str] = set()
    for row in scoring_rows:
        qid = row.get("QuestionID")
        domain = row.get("Domain")
        answer = row.get("AnswerOption")
        if qid not in questions:
            scoring_res.error(f"unknown QuestionID '{qid}' in scoring row")
            continue

        if domain not in domains:
            domain_res.error(f"question '{qid}' references unknown domain '{domain}'")
        else:
            used_domains.add(domain)

        valid_opts = valid_options.get(qid, set())
        if isinstance(answer, str):
            candidate = answer.strip()
        else:
            candidate = ""
        if candidate and candidate not in valid_opts:
            scoring_res.error(f"invalid AnswerOption '{answer}' for question '{qid}'")

        score_value = row.get("ScoreValue")
        if not isinstance(score_value, (int, float)):
            scoring_res.error(
                f"ScoreValue for question '{qid}' / option '{answer}' must be numeric"
            )

        domain_weight = row.get("DomainWeight")
        if not isinstance(domain_weight, (int, float)):
            scoring_res.error(
                f"DomainWeight for question '{qid}' / option '{answer}' must be numeric"
            )

    unused = sorted(domains - used_domains)
    if unused:
        domain_res.warn(f"unused domains: {', '.join(unused)}")

    return questions, valid_options


def _validate_domains(domains_payload: dict, domain_res: CategoryResult) -> Set[str]:
    domain_ids: Set[str] = set()
    for entry in domains_payload.get("domains", []):
        if not isinstance(entry, Mapping):
            domain_res.error("domains entry is not an object")
            continue
        domain_id = entry.get("id")
        if not domain_id:
            domain_res.error("domain missing id")
            continue
        if domain_id in domain_ids:
            domain_res.error(f"duplicate domain id '{domain_id}'")
        domain_ids.add(domain_id)
        cap = entry.get("cap")
        if cap is not None and not isinstance(cap, (int, float)):
            domain_res.error(f"domain '{domain_id}' has non-numeric cap '{cap}'")
    return domain_ids


def _validate_rules(
    rules_payload: dict,
    known_flags: Set[str],
    rules_res: CategoryResult,
) -> None:
    rules_map = rules_payload.get("rules", {})
    order = rules_payload.get("order", [])
    for rule_id in order:
        if rule_id not in rules_map:
            rules_res.error(f"rule '{rule_id}' listed in order but missing definition")
    for rule_id, rule in rules_map.items():
        if not isinstance(rule, Mapping):
            rules_res.error(f"rule '{rule_id}' is not an object")
            continue
        kind = rule.get("kind")
        if kind not in {"override", "floor", "modifier"}:
            rules_res.error(f"rule '{rule_id}' has unknown kind '{kind}'")
            continue

        if kind == "override":
            tier = rule.get("setTier")
            if not isinstance(tier, int):
                rules_res.error(f"rule '{rule_id}' override requires integer setTier")
            elif not (0 <= tier <= 4):
                rules_res.error(f"rule '{rule_id}' setTier {tier} out of range 0..4")
        if kind == "floor":
            tier = rule.get("minTier")
            if not isinstance(tier, int):
                rules_res.error(f"rule '{rule_id}' floor requires integer minTier")
            elif not (0 <= tier <= 4):
                rules_res.error(f"rule '{rule_id}' minTier {tier} out of range 0..4")
        if kind == "modifier":
            delta = rule.get("delta")
            if not isinstance(delta, int):
                rules_res.error(f"rule '{rule_id}' modifier requires integer delta")
            elif not (-3 <= delta <= 3):
                rules_res.error(f"rule '{rule_id}' delta {delta} out of range -3..3")

        for tier_key in ("minTier", "maxTier"):
            if tier_key in rule and not isinstance(rule[tier_key], int):
                rules_res.error(
                    f"rule '{rule_id}' {tier_key} must be integer when present"
                )

        when_expr = str(rule.get("when", "") or "")
        cleaned = re.sub(r"[><=]{1,2}\s*\d+", "", when_expr)
        tokens = IDENT.findall(cleaned)
        for token in tokens:
            if token in {"AND", "OR", "NOT"}:
                continue
            if token not in known_flags:
                rules_res.error(f"rule '{rule_id}' references unknown flag '{token}'")


def _validate_blurbs(
    blurbs_payload: dict,
    questions: Mapping[str, Mapping[str, object]],
    valid_options: Mapping[str, Set[str]],
    blurbs_res: CategoryResult,
) -> None:
    for entry in blurbs_payload.get("byAnswer", []) or blurbs_payload.get(
        "by_answer", []
    ):
        if not isinstance(entry, Mapping):
            blurbs_res.error("blurbs byAnswer entry is not an object")
            continue
        qid = entry.get("QuestionID")
        answer = entry.get("AnswerOption")
        if qid not in questions:
            blurbs_res.error(f"unknown QuestionID '{qid}' in blurbs")
            continue
        if answer not in valid_options.get(qid, set()):
            blurbs_res.error(
                f"invalid AnswerOption '{answer}' for question '{qid}' in blurbs"
            )

    allowed_tiers = {
        "In-Home Care",
        "Assisted Living",
        "Memory Care",
        "Memory Care High Acuity",
    }
    by_tier = blurbs_payload.get("byTier") or blurbs_payload.get("by_tier") or {}
    unknown = sorted(set(by_tier.keys()) - allowed_tiers)
    if unknown:
        blurbs_res.warn(f"unknown tiers in blurbs.byTier: {', '.join(unknown)}")


def main() -> int:
    categories = {
        "Schema": CategoryResult("Schema"),
        "Domains": CategoryResult("Domains"),
        "Scoring": CategoryResult("Scoring"),
        "Rules": CategoryResult("Rules"),
        "Blurbs": CategoryResult("Blurbs"),
    }
    try:
        schema = _load_json("schema.json")
        scoring_payload = _load_json("scoring.json")
        rules_payload = _load_json("rules.json")
        domains_payload = _load_json("domains.json")
        blurbs_payload = _load_json("blurbs.json")
    except RuntimeError as exc:
        print(f"❌ bootstrap: {exc}")
        return 1

    scoring_rows = scoring_payload.get("scoring", [])
    if not isinstance(scoring_rows, list):
        print("❌ scoring: payload missing 'scoring' array")
        return 1

    domain_ids = _validate_domains(domains_payload, categories["Domains"])
    questions, valid_options = _validate_schema_and_scoring(
        schema,
        scoring_rows,
        domain_ids,
        categories["Schema"],
        categories["Scoring"],
        categories["Domains"],
    )

    known_flags = _collect_flags(scoring_rows)
    _validate_rules(rules_payload, known_flags, categories["Rules"])
    _validate_blurbs(blurbs_payload, questions, valid_options, categories["Blurbs"])

    overall_ok = all(cat.ok for cat in categories.values())

    for cat in categories.values():
        for err in cat.errors:
            print(f"❌ {cat.name}: {err}")
        for warn in cat.warnings:
            print(f"⚠️  {cat.name}: {warn}")

    print("\nSummary")
    for cat in categories.values():
        if cat.errors:
            msg = f"{cat.name:<12}: ❌ {cat.errors[0]}"
            if len(cat.errors) > 1:
                msg += f" (+{len(cat.errors) - 1} more)"
        else:
            msg = f"{cat.name:<12}: ✅"
            if cat.warnings:
                msg += f" ({'; '.join(cat.warnings)})"
        print(msg)

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
