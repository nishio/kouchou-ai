"""
Opinion classification step plugin.

Attaches independent yes/no labels (hate_or_insult, policy_proposal, ...) to each
extracted opinion using an LLM.
"""

from typing import Any

from analysis_core.plugin import (
    StepContext,
    StepInputs,
    StepOutputs,
    step_plugin,
)
from analysis_core.plugins.builtin._legacy_config import build_legacy_runtime_config


@step_plugin(
    id="analysis.opinion_classification",
    version="1.0.0",
    name="Opinion Classification",
    description="Label each extracted opinion with independent yes/no flags using LLM",
    inputs=["arguments"],
    outputs=["classifications", "classification_summary"],
    use_llm=True,
)
def opinion_classification_plugin(
    ctx: StepContext,
    inputs: StepInputs,
    config: dict[str, Any],
) -> StepOutputs:
    """
    Classify extracted opinions.

    Config options:
        - model: LLM model to use (default: from context)
        - prompt: System prompt with the label definitions
        - workers: Number of parallel requests
        - labels: Label IDs expected in each response (default: built-in labels)
        - timeout_seconds: Per-request timeout
    """
    from analysis_core.prompts import get_default_prompt
    from analysis_core.steps.opinion_classification import (
        CLASSIFICATIONS_FILENAME,
        SUMMARY_FILENAME,
    )
    from analysis_core.steps.opinion_classification import (
        opinion_classification as classification_impl,
    )

    step_config = config.get("opinion_classification", config)
    legacy_config = build_legacy_runtime_config(ctx, inputs, include_token_usage=True)
    legacy_config["opinion_classification"] = {
        "model": step_config.get("model") or ctx.model,
        "prompt": step_config.get("prompt") or get_default_prompt("opinion_classification"),
        "workers": step_config.get("workers", 1),
        "labels": step_config.get("labels"),
        "timeout_seconds": step_config.get("timeout_seconds"),
    }

    classification_impl(legacy_config)

    return StepOutputs(
        artifacts={
            "classifications": ctx.output_dir / CLASSIFICATIONS_FILENAME,
            "classification_summary": ctx.output_dir / SUMMARY_FILENAME,
        },
        token_usage=legacy_config.get("total_token_usage", 0),
        token_input=legacy_config.get("token_usage_input", 0),
        token_output=legacy_config.get("token_usage_output", 0),
    )
