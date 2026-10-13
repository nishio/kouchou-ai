"""Label definitions, prompt builder and response parser for opinion classification.

This module intentionally depends on the standard library only, so that the same
label definitions and prompt can be reused by lightweight scripts (for example a
runner that talks to a local LLM without installing the full package).
"""

import json
import re
from dataclasses import dataclass

YES = "yes"
NO = "no"

_CODE_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)
_TRUE_STRINGS = frozenset({"true", "yes", "1"})
_FALSE_STRINGS = frozenset({"false", "no", "0"})


@dataclass(frozen=True)
class OpinionLabel:
    """One independent yes/no label attached to each extracted opinion."""

    id: str
    name: str
    includes: str
    excludes: str


DEFAULT_LABELS: tuple[OpinionLabel, ...] = (
    OpinionLabel(
        id="hate_or_insult",
        name="侮辱・ヘイト表現",
        includes=(
            "特定の個人または集団に対する侮辱・罵倒・蔑称・人格否定（例:「無能」「クズ」「バカ」「気持ち悪い」）、"
            "国籍・民族・出身地域・性別・年齢・宗教・障害などの属性を理由にした差別・排除・敵意の表明、"
            "個人や集団に危害・不幸が及ぶことを望む表現。"
        ),
        excludes=(
            "政策・行為・発言に対する強い批判や不信（根拠の有無を問わない）、"
            "辞任・逮捕・処罰・捜査などを求める要求（侮辱表現を伴わない場合）、"
            "皮肉・不満・失望の表明、事実の指摘。"
        ),
    ),
    OpinionLabel(
        id="policy_proposal",
        name="政策・制度への提案",
        includes=(
            "政府・自治体・議会・司法・公的機関・政党などが扱う公共の政策・制度・法律・行政運営について、"
            "「〜すべき」「〜してほしい」「〜が必要」「〜に反対」など、取るべき対応や方向性を具体的に述べているもの。"
            "制度の新設・廃止・改革の要求、運用の変更要求、特定の政策や法案への明示的な賛否を含む。"
        ),
        excludes=(
            "人物や団体の評価・感想、事実の記述、疑問や質問、感情の表明、"
            "特定の人物の辞任・逮捕・処罰・起用など人事や個人への対応だけを求めるもの、"
            "番組・出演者・メディアの進行に関する要望など公共政策と関係しないもの、"
            "対象や内容が特定できない漠然とした不満。"
        ),
    ),
)

DEFAULT_LABEL_IDS: tuple[str, ...] = tuple(label.id for label in DEFAULT_LABELS)

_PROMPT_HEADER = """あなたは意見分類の補助者です。userのinputは、ある文章から抽出された1件の意見（短い主張）です。
この意見が以下の各ラベルの定義に該当するかどうかを判定し、JSONで返してください。

# 判定のルール
- 各ラベルは互いに独立しています。複数のラベルに該当することも、どれにも該当しないこともあります。
- 意見の内容を書き換えたり、要約したり、良し悪しを評価したりしないでください。定義に当てはまるかどうかだけを判定します。
- 意見の主張に賛成か反対かは判定に影響させないでください。
- 判断に迷う場合は、定義の「該当」に明確に当てはまるときだけ true にしてください。
- 出力はJSONオブジェクトのみとし、各ラベルIDをキー、true または false を値にしてください。説明文は出力しないでください。
"""

_PROMPT_EXAMPLES = """
# 入出力の例（説明用に作成した架空の例です。実際の入力と混同しないでください）
/human
バスの本数を増やしてほしい。
/ai
{"hate_or_insult": false, "policy_proposal": true}

/human
あの大臣は本当に無能でどうしようもない。
/ai
{"hate_or_insult": true, "policy_proposal": false}

/human
○○人は全員この国から追い出すべきだ。
/ai
{"hate_or_insult": true, "policy_proposal": true}

/human
昨日の放送は面白かった。
/ai
{"hate_or_insult": false, "policy_proposal": false}

/human
検察改革は必要だが、拙速に進めるべきではない。
/ai
{"hate_or_insult": false, "policy_proposal": true}

/human
大臣は責任を取って辞任すべきだ。
/ai
{"hate_or_insult": false, "policy_proposal": false}
"""


def build_classification_prompt(labels: tuple[OpinionLabel, ...] | list[OpinionLabel] = DEFAULT_LABELS) -> str:
    """Build the system prompt from label definitions.

    The few-shot examples are written for the default labels. When a different
    label set is supplied the examples are omitted so they do not teach keys that
    the parser will not accept.
    """
    if not labels:
        raise ValueError("at least one label is required")
    sections = [_PROMPT_HEADER, "\n# ラベル定義\n"]
    for label in labels:
        sections.append(f"## {label.id}（{label.name}）\n- 該当: {label.includes}\n- 非該当: {label.excludes}\n\n")
    sections.append("# 出力形式\n")
    sections.append(json.dumps({label.id: False for label in labels}, ensure_ascii=False) + "\n")
    if tuple(label.id for label in labels) == DEFAULT_LABEL_IDS:
        sections.append(_PROMPT_EXAMPLES)
    return "".join(sections)


class InvalidClassificationResponse(ValueError):
    """The LLM response does not contain a boolean for every expected label."""


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_STRINGS:
            return True
        if normalized in _FALSE_STRINGS:
            return False
    raise InvalidClassificationResponse("ラベル値が真偽値ではありません")


def parse_classification_response(response: str | dict, label_ids: tuple[str, ...] | list[str]) -> dict[str, bool]:
    """Parse a classification response into ``{label_id: bool}``.

    Malformed output raises ``InvalidClassificationResponse``; it is never treated
    as "all labels false", so a failed judgement cannot silently become a result.
    """
    if isinstance(response, dict):
        data = response
    elif isinstance(response, str):
        text = _CODE_FENCE.sub("", response).strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if match is None:
                raise InvalidClassificationResponse("分類応答にJSONオブジェクトが含まれていません") from None
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                raise InvalidClassificationResponse("分類応答のJSONが不正です") from None
    else:
        raise InvalidClassificationResponse("分類応答の型が不正です")

    if not isinstance(data, dict):
        raise InvalidClassificationResponse("分類応答がオブジェクトではありません")

    result: dict[str, bool] = {}
    for label_id in label_ids:
        if label_id not in data:
            raise InvalidClassificationResponse(f"分類応答にラベル '{label_id}' がありません")
        result[label_id] = _coerce_bool(data[label_id])
    return result


def format_label_value(flag: bool) -> str:
    """Render a boolean label as the attribute value shown in viewers."""
    return YES if flag else NO


def compute_label_ratios(
    rows: list[dict[str, bool]] | list[dict[str, str]], label_ids: tuple[str, ...] | list[str]
) -> dict[str, object]:
    """Count how many opinions carry each label and the share of the total.

    ``rows`` may hold booleans or the ``yes``/``no`` strings written to CSV.
    The ratio is relative to the opinions that were classified, which is the set
    of extracted opinions, not the original comments nor any population.
    """
    total = len(rows)
    labels: dict[str, dict[str, float | int]] = {}
    for label_id in label_ids:
        count = 0
        for row in rows:
            value = row.get(label_id)
            if value is True or (isinstance(value, str) and value.strip().lower() in _TRUE_STRINGS):
                count += 1
        labels[label_id] = {"count": count, "ratio": (count / total) if total else 0.0}
    return {"total": total, "labels": labels}
