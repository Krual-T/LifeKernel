import argparse
import asyncio
import json
from typing import Dict, List

from src.agents import AgentSpec
from src.orchestrator import ManualProvider, MockProvider, Orchestrator


def _load_config(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_agents(raw_agents: List[Dict[str, object]]) -> List[AgentSpec]:
    agents: List[AgentSpec] = []
    for raw in raw_agents:
        agents.append(
            AgentSpec(
                name=str(raw.get("name")),
                role=str(raw.get("role")),
                goal=str(raw.get("goal")),
                max_tokens=int(raw.get("max_tokens", 1200)),
            )
        )
    return agents


def _build_provider(cfg: Dict[str, object]):
    provider_type = str(cfg.get("type", "mock"))
    if provider_type == "manual":
        return ManualProvider()
    seed = int(cfg.get("seed", 7))
    return MockProvider(seed=seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep Research Orchestrator")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    config = _load_config(args.config)
    agents = _build_agents(config.get("agents", []))
    provider = _build_provider(config.get("provider", {}))
    output_dir = str(config.get("output_dir", "workspace/lab/deep_research/outputs"))
    run_id = str(config.get("run_id", "")).strip() or None

    orchestrator = Orchestrator(
        topic=str(config.get("topic")),
        agents=agents,
        provider=provider,
        tools_config=config.get("tools", {}),
        output_dir=output_dir,
        run_id=run_id,
    )

    result = asyncio.run(orchestrator.run())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
