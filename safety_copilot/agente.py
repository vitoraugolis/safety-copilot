#!/usr/bin/env python3
"""Single agent governed by the `analise-seguranca` skill.

Replaces the five-role panel. Two decisions carry the design:

  · The skill's A→B gate is a PROCESS BOUNDARY. Phase A is assembled by
    `contexto.py`, in Python, because the skill itself says the context block
    "can be audited by inspection … there is no reasoning to question". If a
    language model assembles phase A, that sentence is false. The agent
    receives phase A closed and runs phase B only.

  · Isolation is STRUCTURAL, not instructional. Phase B runs in a fresh
    `claude -p` session with no tools at all, in a dedicated empty CLI profile
    (no plugins, hooks, memory, MCP or settings from the development machine),
    from an empty temporary directory. The skill, references and diagram are
    passed as text — the same approved material the Astra run received. Each
    session's init event is checked; anything it had beyond that text rejects
    the analysis. Instruction is advice; absence is a guarantee.

    CLAUDE_CONFIG_DIR=~/.claude-blind claude auth login     # once, by the user
    python3 -m safety_copilot.agente --run RUN_A              # new blind run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from . import blind_feed as bf
from . import contexto as ctx

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
REFS = ROOT / ".agents" / "skills" / "analise-seguranca" / "references"
SAIDA = ROOT / "state" / "analises"
CLI = shutil.which("claude") or "claude"
TIMEOUT_S = 900
MODELO = "claude-opus-5"
# Dedicated, empty CLI profile for blind runs: no plugins, hooks, memory, MCP or
# settings of the development environment. Logged in once, by the user.
PERFIL = Path.home() / ".claude-blind"
ISOLAMENTO = ["--safe-mode", "--tools", "", "--strict-mcp-config",
              "--disable-slash-commands", "--no-session-persistence"]
# Same wording as the Astra run, so both models receive the same instructions.
POLITICA = ("You are the process safety analyst. Perform Phase B using only the supplied "
            "Phase A and design references. Do not call tools or access any files, memory, "
            "other conversations, network, or external sources. All authorized material "
            "is included verbatim below. Return only the report requested by the user.")

# The invocation message carries what belongs to the EXPERIMENT, not to the
# method — which is why it does not live in SKILL.md.
PROMPT = """Phase A of this analysis has already been executed by deterministic code
and is closed in the block below. Your task is **phase B** of the skill: interpret.

Rules for this run:

1. The plant is anonymous. Do not speculate about its identity, the origin of the
   data or any benchmark. If you recognise something, ignore it: speculation does
   not enter the report.
2. Do NOT recompute or retype phase A's figures where a field carries them. Cite
   the field. A retyped figure is a figure that can diverge from the database.
3. Do NOT write files. Return the report as your final answer, in markdown.
4. Write only the phase B sections of the skill's output format:
   `# <required decision in one sentence>`, `## Fact`, `## Scenario and mechanism`,
   `## Analysis` (1. Bowtie, 2. Process, 3. Context), `## Risk judgement`,
   `## Recommendation`, `## Evidence and assumptions`. The phase A context is not
   yours to write: it is already in the audit log.
5. This is one analysis in a stream. It is dated at `t_now`; you know nothing that
   happens after it. Say what this trigger changed.
6. Be concise. Every claim needs a source in the phase A block or in a skill
   reference. A sentence without a source does not go in.
7. Write in English.

You may read `SKILL.md` and the files in `references/` in this directory.

---

{contexto}
"""


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def preparar(run: str, ts: str | None = None, motivos: list | None = None,
             incident_id: str | None = None, destino: Path | None = None) -> dict:
    """Phase A only: freeze the context, write it and the prompt. No model call."""
    c = ctx.montar(run, ts, incident_id, gatilho=motivos)
    d = destino or (SAIDA / c["identidade"]["incident_id"])
    d.mkdir(parents=True, exist_ok=True)
    ctx_md = ctx.render_md(c)
    bf.scrub(ctx_md)
    (d / "context.json").write_text(json.dumps(c, ensure_ascii=False, indent=2))
    (d / "context.md").write_text(ctx_md)
    prompt = PROMPT.format(contexto=ctx_md)
    bf.scrub(prompt)
    (d / "prompt.md").write_text(prompt)
    return {"dir": d, "contexto": c, "prompt": prompt}


def _isolado(cmd: list[str], entrada: str, cwd: Path) -> tuple[str, str, int]:
    """Run the CLI in the dedicated blind profile, with nothing inherited from here."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    env["CLAUDE_CONFIG_DIR"] = str(PERFIL)
    try:
        proc = subprocess.run(cmd, input=entrada, cwd=cwd, env=env, capture_output=True,
                              text=True, timeout=TIMEOUT_S)
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"timeout after {TIMEOUT_S}s", -1


def _eventos(bruto: str) -> list[dict]:
    out = []
    for linha in bruto.splitlines():
        try:
            out.append(json.loads(linha))
        except json.JSONDecodeError:
            pass
    return out


def _isolamento(eventos: list[dict]) -> list[str]:
    """What the session had besides the text we gave it. Empty list = isolated."""
    init = next((e for e in eventos if e.get("subtype") == "init"), None)
    if not init:
        return ["no init event"]
    fora = [f"{k}={init.get(k)}" for k in ("tools", "mcp_servers", "skills", "plugins",
                                           "slash_commands") if init.get(k)]
    usos = [b for e in eventos if e.get("type") == "assistant"
            for b in e["message"].get("content", []) if b.get("type") == "tool_use"]
    return fora + [f"tool_use x{len(usos)}"] * bool(usos)


def analisar(run: str, ts: str | None = None, motivos: list | None = None,
             incident_id: str | None = None, modelo: str | None = None,
             destino: Path | None = None) -> dict:
    """Phase B by a fresh, text-only Claude session. This is what the stream calls.

    Same approved inputs as the Astra run (astra.approved_material), passed as
    text: no tools, no files, no MCP, no plugins, no memory, dedicated profile.
    Any gate that fails stops the run instead of writing a report.
    """
    from .astra import approved_material        # identical inputs across models
    modelo = modelo or MODELO
    material = approved_material()
    policy = (POLITICA + "\n\n" + "\n\n".join(
        f"<document path=\"{k}\">\n{v}\n</document>" for k, v in material.items()))
    d0 = Path(destino) if destino else None
    if d0 and (d0 / "meta.json").exists():
        meta0 = json.loads((d0 / "meta.json").read_text())
        if meta0.get("ok") and meta0.get("blind") and meta0.get("model") == modelo \
                and (d0 / "phase_b.md").exists():
            # Resume: keep an accepted answer only if phase A is byte-identical.
            c = ctx.montar(run, ts, incident_id, gatilho=motivos)
            if json.dumps(c, ensure_ascii=False, indent=2) != (d0 / "context.json").read_text():
                raise RuntimeError(f"Phase A changed since {d0.name} was accepted; start a new run")
            if policy != (d0 / "system.md").read_text():
                raise RuntimeError(f"Skill or references changed since {d0.name} was accepted; "
                                   "start a new run")
            print(f"     kept accepted analysis {d0.name}", flush=True)
            return {"dir": d0, "ok": True, "phase_b": (d0 / "phase_b.md").read_text(),
                    "contexto": c, "seconds": 0, "meta": meta0}
        # A rejected attempt stays in the run's audit trail, then the analysis is retried.
        carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        arquivo = d0.parent / "audit" / "failed_attempts" / f"{d0.name}_{carimbo}"
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(d0), arquivo)
    res = preparar(run, ts, motivos, incident_id, destino)
    c, d = res["contexto"], res["dir"]
    for nome, conteudo in material.items():
        f = d / "input" / nome
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(conteudo)
    prompt = res["prompt"].replace(
        "You may read `SKILL.md` and the files in `references/` in this directory.",
        "The skill, references and diagram are supplied in the system instructions. "
        "No tools are needed or permitted. The JSON below carries the exact field paths.")
    prompt += ("\n\n<phase_a_json>\n" + json.dumps(c, ensure_ascii=False, indent=2)
               + "\n</phase_a_json>\n")
    if bf._FORBIDDEN_RE.search(prompt) or bf._FORBIDDEN_RE.search(policy):
        raise RuntimeError("Unmasked provenance in the exact model input")
    (d / "system.md").write_text(policy)
    (d / "prompt.md").write_text(prompt)

    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="sc-opus-") as tmp:
        (Path(tmp) / "system.md").write_text(policy)
        cmd = [CLI, "-p", *ISOLAMENTO, "--model", modelo,
               "--system-prompt-file", str(Path(tmp) / "system.md"),
               "--output-format", "stream-json", "--verbose"]
        bruto, err, rc = _isolado(cmd, prompt, Path(tmp))
    dur = time.time() - t0
    (d / "transcript.jsonl").write_text(bruto)
    (d / "stderr.txt").write_text(err)

    eventos = _eventos(bruto)
    fim = next((e for e in eventos if e.get("type") == "result"), {})
    fase_b = fim.get("result") or "" if fim.get("subtype") == "success" and not fim.get("is_error") else ""
    modelos = {e["message"].get("model") for e in eventos if e.get("type") == "assistant"}
    fora = _isolamento(eventos)
    secoes = ("## Fact", "## Scenario and mechanism", "## Analysis",
              "## Risk judgement", "## Recommendation", "## Evidence and assumptions")
    ok = (rc == 0 and bool(fase_b) and not fora and modelos == {modelo}
          and all(x in fase_b for x in secoes) and not bf._FORBIDDEN_RE.search(fase_b))
    meta = {
        "incident_id": c["identidade"]["incident_id"], "run": run, "ts": c["identidade"]["ts"],
        "trigger": motivos or [], "ok": ok, "blind": ok, "rc": rc, "seconds": round(dur, 1),
        "phase_b_by": "claude -p, fresh text-only session (dedicated profile, no tools, "
                      "no MCP, no plugins, no memory)" if ok else None,
        "model": modelo, "models_in_session": sorted(m for m in modelos if m),
        "isolation_breaks": fora, "session_id": fim.get("session_id"),
        "usage": fim.get("usage") or {},
        "cli_version": subprocess.run([CLI, "--version"], capture_output=True,
                                      text=True).stdout.strip(),
        "sha_inputs": {str(f.relative_to(d)): _sha(f) for f in sorted((d / "input").rglob("*"))
                       if f.is_file()},
        "sha_system": _sha(d / "system.md"), "sha_prompt": _sha(d / "prompt.md"),
        "sha_context": _sha(d / "context.json"), "database": bf.DB.name,
        "error": None if ok else (str(fim.get("result")) + " " + err)[-2000:],
    }
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    if not ok:
        raise RuntimeError(f"Phase B rejected at {d.name}: {meta['error'][:300]} "
                           f"isolation={fora} models={sorted(m for m in modelos if m)}")
    (d / "phase_b.md").write_text(fase_b)
    print(f"     {modelo} complete: {meta['seconds']}s, text-only session", flush=True)
    return {"dir": d, "ok": ok, "phase_b": fase_b, "contexto": c,
            "seconds": meta["seconds"], "meta": meta}


def replay(run: str = "RUN_A", modelo: str = MODELO, retomar: Path | None = None) -> Path:
    """New blind run in its own directory, or resume one (accepted answers are kept)."""
    global SAIDA
    from . import stream
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Fail before the stream if the profile is not logged in or not isolated.
    with tempfile.TemporaryDirectory(prefix="sc-opus-") as tmp:
        bruto, err, rc = _isolado([CLI, "-p", *ISOLAMENTO, "--model", modelo,
                                   "--system-prompt", "Reply with OK.",
                                   "--output-format", "stream-json", "--verbose"],
                                  "OK?", Path(tmp))
    ev = _eventos(bruto)
    fim = next((e for e in ev if e.get("type") == "result"), {})
    modelos = {e["message"].get("model") for e in ev if e.get("type") == "assistant"}
    preflight = json.dumps(
        {"rc": rc, "result": fim.get("result"), "is_error": fim.get("is_error"),
         "isolation_breaks": _isolamento(ev), "models": sorted(m for m in modelos if m)},
        ensure_ascii=False, indent=2)
    if rc or fim.get("is_error") or _isolamento(ev) or modelos != {modelo}:
        raise SystemExit(f"preflight failed: {preflight}\n"
                         f"log in the blind profile first: CLAUDE_CONFIG_DIR={PERFIL} claude auth login")
    if retomar:
        saida = Path(retomar).resolve()
        if not (saida / "preflight.json").exists():
            raise SystemExit(f"not a run folder: {saida}")
        (saida / f"preflight_resume_{carimbo}.json").write_text(preflight)
    else:
        saida = SAIDA / f"{run}_{modelo.upper().replace('-', '_')}_{carimbo}"
        saida.mkdir(parents=True)
        (saida / "preflight.json").write_text(preflight)
    print(f"OUTPUT {saida}", flush=True)
    SAIDA = saida
    stream.SAIDA = saida / "stream"
    stream.rodar(run, modo="completa", modelo=modelo)
    return saida


def main() -> None:
    ap = argparse.ArgumentParser(prog="python3 -m safety_copilot.agente")
    ap.add_argument("--run", default="RUN_A")
    ap.add_argument("--modelo", default=MODELO)
    ap.add_argument("--resume", type=Path, default=None,
                    help="run folder to resume; accepted analyses are kept")
    a = ap.parse_args()
    # Under `python -m` this file is __main__; the stream reads SAIDA from the
    # package module, so replay must run there or the output folder is ignored.
    from . import agente
    agente.replay(a.run, a.modelo, a.resume)


if __name__ == "__main__":
    main()
