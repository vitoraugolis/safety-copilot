"""Replay through fresh GPT-6 Astra sessions with only approved input text.

Usage: python3 -m safety_copilot.astra
Each execution creates a new directory; existing analyses are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from . import agente, blind_feed as bf, stream

MODEL = "gpt-6-astra"
DISABLED = (
    "shell_tool", "unified_exec", "apps", "plugins", "memories", "multi_agent",
    "multi_agent_v2", "browser_use", "browser_use_external", "computer_use",
    "in_app_browser", "image_generation", "view_image", "hooks", "skill_search",
    "code_mode", "code_mode_host", "goals", "sleep_tool", "workspace_dependencies",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def approved_material() -> dict[str, str]:
    """Preserve the method; exclude worked findings from previous episodes."""
    material = {"SKILL.md": agente.SKILL.read_text()}
    material.update({"references/" + p.name: p.read_text()
                     for p in sorted(agente.REFS.glob("*.md"))})
    key = "references/cross-checks.md"
    s = material[key]
    # The episode findings were removed from the source file itself (2026-09-15);
    # this stays as a guard in case they come back.
    if "On the reference reactor episode" in s or "**Worked case.**" in s:
        raise ValueError("Episode findings back in cross-checks.md; review the reference")
    material[key] = s
    material["diagrams/BT-REATOR.txt"] = (agente.ROOT / "diagrams/BT-REATOR.txt").read_text()
    return {k: bf.scrub(v) for k, v in material.items()}


def execute(run: str, ts=None, motivos=None, incident_id=None, modelo=None,
            destino=None) -> dict:
    """Adapter for stream.rodar; each call has a fresh, unresumed session."""
    d = Path(destino)
    if d.exists():
        raise FileExistsError(f"Refusing to overwrite {d}")
    res = agente.preparar(run, ts, motivos, incident_id, d)
    c = res["contexto"]
    material = approved_material()
    snapshot = d / "input"
    for name, content in material.items():
        p = snapshot / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    policy = (
        "You are the process safety analyst. Perform Phase B using only the supplied "
        "Phase A and design references. Do not call tools or access any files, memory, "
        "other conversations, network, or external sources. All authorized material "
        "is included verbatim below. Return only the report requested by the user.\n\n"
        + "\n\n".join(f"<document path=\"{k}\">\n{v}\n</document>"
                       for k, v in material.items())
    )
    (d / "system.md").write_text(policy)
    # JSON supplies the exact field names and unrounded values; the project's
    # Markdown is still retained as the auditable human view of the same context.
    prompt = res["prompt"].replace(
        "You may read `SKILL.md` and the files in `references/` in this directory.",
        "The skill, references and diagram are supplied in the system instructions. "
        "No tools are needed or permitted. The JSON below carries the exact field paths.")
    prompt += "\n\n<phase_a_json>\n" + json.dumps(c, ensure_ascii=False, indent=2) + "\n</phase_a_json>\n"
    if bf._FORBIDDEN_RE.search(prompt) or bf._FORBIDDEN_RE.search(policy):
        raise RuntimeError("Unmasked provenance in the exact model input")
    (d / "prompt.md").write_text(prompt)
    cli = shutil.which("codex")
    if not cli:
        raise RuntimeError("Codex CLI unavailable")
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="sc-astra-") as tmp:
        tmp = Path(tmp)
        home, cwd = tmp / "runtime", tmp / "input"
        home.mkdir(); cwd.mkdir()
        original_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        auth = original_home / "auth.json"
        if not auth.exists():
            raise RuntimeError("Codex authentication unavailable in the configured home")
        (home / "auth.json").symlink_to(auth)
        cfg = ('model = "gpt-6-astra"\nmodel_reasoning_effort = "high"\n'
               'web_search = "disabled"\nproject_doc_max_bytes = 0\n'
               '[features]\n' + ''.join(f'{k} = false\n' for k in DISABLED))
        # Disable skill discovery entries as well; no project or user memory is input.
        skill_paths = list((Path.home() / ".agents/skills").glob("*/SKILL.md"))
        skill_paths += [home / "skills/.system" / name / "SKILL.md"
                        for name in ("imagegen", "openai-docs", "plugin-creator", "skill-creator", "skill-installer")]
        cfg += ''.join('\n[[skills.config]]\npath = ' + json.dumps(str(p)) + '\nenabled = false\n'
                       for p in skill_paths)
        (home / "config.toml").write_text(cfg)
        (cwd / "system.md").write_text(policy)
        (d / "runtime_config.toml").write_text(cfg)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CODEX_", "OPENAI_"))}
        env["CODEX_HOME"] = str(home)
        overrides = ["-c", f'model_instructions_file="{cwd / "system.md"}"']
        probe = subprocess.run([cli, "debug", "prompt-input", *overrides, "Analyze supplied context only."],
                               cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
        if probe.returncode:
            raise RuntimeError(probe.stderr[-2000:])
        (d / "environment_prompt.json").write_text(probe.stdout)
        for forbidden in ("MEMORY_SUMMARY", "gabarito/", "BLIND_TEST_PROTOCOL", "METHODOLOGY.md", "rollout_summaries"):
            if forbidden in probe.stdout:
                raise RuntimeError("Unexpected environment context: " + forbidden)
        cmd = [cli, "exec", "--strict-config", "--skip-git-repo-check", "--ignore-rules",
               "-s", "read-only", "-m", MODEL, *overrides, "--json", "-"]
        (d / "command.json").write_text(json.dumps(cmd, indent=2))
        try:
            proc = subprocess.run(cmd, input=prompt, cwd=cwd, env=env,
                                  capture_output=True, text=True, timeout=agente.TIMEOUT_S)
            raw, err, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or b""
            raw = raw.decode() if isinstance(raw, bytes) else raw
            err, rc = "timeout", -1
        (d / "transcript.jsonl").write_text(raw)
        (d / "stderr.txt").write_text(err)
        events = [json.loads(line) for line in raw.splitlines() if line.strip()]
        sid = next((e["thread_id"] for e in events if e["type"] == "thread.started"), None)
        tool_items = [e for e in events if e.get("item", {}).get("type") not in
                      (None, "agent_message", "reasoning", "error")]
        messages = [e["item"]["text"] for e in events if e["type"] == "item.completed"
                    and e.get("item", {}).get("type") == "agent_message"]
        phase_b = messages[-1] if messages else ""
        completed = next((e for e in events if e["type"] == "turn.completed"), None)
        confirmed_models = set()
        for path in (home / "sessions").rglob("*.jsonl"):
            for line in path.read_text().splitlines():
                record = json.loads(line)
                if record.get("type") == "turn_context":
                    model = record.get("payload", {}).get("model")
                    if model:
                        confirmed_models.add(model)
            shutil.copy(path, d / "session.jsonl")
        sections = ("## Fact", "## Scenario and mechanism", "## Analysis",
                    "## Risk judgement", "## Recommendation", "## Evidence and assumptions")
        ok = (rc == 0 and completed is not None and not tool_items
              and confirmed_models == {MODEL} and all(s in phase_b for s in sections))
        if bf._FORBIDDEN_RE.search(phase_b):
            raise RuntimeError("Provenance term in the model output; reject this analysis")
        meta = {"incident_id": c["identidade"]["incident_id"], "run": run,
                "ts": c["identidade"]["ts"], "trigger": motivos or [], "ok": ok,
                "rc": rc, "seconds": round(time.monotonic() - t0, 1),
                "phase_b_by": "Codex CLI, fresh text-only GPT-6 Astra session",
                "blind": ok, "model": MODEL, "models_in_session": sorted(confirmed_models),
                "session_id": sid, "usage": (completed or {}).get("usage", {}),
                "tool_items": tool_items, "database": bf.DB.name,
                "sha_database": sha(bf.DB), "sha_skill": sha(snapshot / "SKILL.md"),
                "sha_inputs": {str(p.relative_to(d)): sha(p) for p in snapshot.rglob("*") if p.is_file()},
                "sha_system": sha(d / "system.md"), "sha_prompt": sha(d / "prompt.md"),
                "sha_context": sha(d / "context.json"),
                "cli_version": subprocess.run([cli, "--version"], capture_output=True, text=True).stdout.strip(),
                "error": None if ok else "Completion, model, tools, or report-format gate failed; inspect transcript"}
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        if not ok:
            raise RuntimeError(f"Astra analysis failed: {d}; {meta['error']}")
        (d / "phase_b.md").write_text(phase_b)
        reports = d / "reports"
        reports.mkdir()
        (reports / (meta["incident_id"] + ".md")).write_text(phase_b)
    print(f"     Astra complete: {meta['seconds']}s; no tool calls; model {MODEL}", flush=True)
    return {"dir": d, "ok": ok, "phase_b": phase_b, "contexto": c, "meta": meta}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=Path, help="Resume an existing Astra execution without repeating accepted answers")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.resume.resolve() if args.resume else agente.SAIDA / f"RUN_A_GPT6_ASTRA_{stamp}"
    if args.resume:
        if not out.is_dir() or (out / "INVALIDATED.json").exists():
            raise ValueError("Resume requires an existing, non-invalidated execution")
    else:
        out.mkdir(exist_ok=False)
    print(f"OUTPUT {out}", flush=True)
    agente.SAIDA = out

    def resume_or_execute(*a, **kw):
        d = Path(kw["destino"])
        if args.resume and d.exists():
            mp = d / "meta.json"
            meta = json.loads(mp.read_text()) if mp.exists() else {}
            if meta.get("ok") and meta.get("blind"):
                if (meta.get("model") != MODEL or meta.get("sha_database") != sha(bf.DB)
                        or meta.get("sha_context") != sha(d / "context.json")
                        or meta.get("sha_prompt") != sha(d / "prompt.md")):
                    raise RuntimeError(f"Accepted analysis provenance changed: {d}")
                print(f"     preserved accepted analysis: {d.name}", flush=True)
                return {"dir": d, "ok": True,
                        "phase_b": (d / "phase_b.md").read_text(),
                        "contexto": json.loads((d / "context.json").read_text()), "meta": meta}
            archive = out / "audit" / "failed_attempts" / f"{d.name}_{stamp}"
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), archive)
        return execute(*a, **kw)

    agente.analisar = resume_or_execute
    stream.SAIDA = out / "stream"
    stream.rodar("RUN_A", modo="completa", modelo=MODEL)


if __name__ == "__main__":
    main()
