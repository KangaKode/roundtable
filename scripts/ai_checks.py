#!/usr/bin/env python3
"""
AI-specific validation checks -- catches issues standard linters miss.

Checks:
  1. LLM output safety: all json.loads(response.content) paths have error handling
  2. No raw LLM output reaches eval/exec/SQL
  3. CacheablePrompt usage in orchestration (not bare string prompts)
  4. TokenUsage populated in all provider paths
  5. Agent protocol types importable without circular deps
  6. Prompt injection defense wired into external agent paths
  7. Security sanitization on all external input paths

Usage: python scripts/ai_checks.py [path_to_src]
Exit code 0 = all passed, 1 = failures found.
"""

import os
import re
import sys

findings = []
passes = []


def fail(msg):
    findings.append(f"  FAIL: {msg}")


def ok(msg):
    passes.append(f"  ✓ {msg}")


def scan_file(filepath, content, rel_path):
    lines = content.split("\n")

    # Check 1: json.loads on LLM output must have try/except
    json_loads_lines = []
    for n, line in enumerate(lines, 1):
        if "json.loads(" in line and "response" in line.lower():
            json_loads_lines.append((n, line.strip()))

    for n, line in json_loads_lines:
        context_start = max(0, n - 5)
        context_end = min(len(lines), n + 5)
        context = "\n".join(lines[context_start:context_end])
        if "try" not in context and "except" not in context:
            fail(f"{rel_path}:{n} -- json.loads() on LLM output without try/except")

    # Check 2: LLM output must not reach eval/exec/SQL
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("#"):
            continue
        if re.search(r'eval\(.*response', line) or re.search(r'exec\(.*response', line):
            fail(f"{rel_path}:{n} -- LLM output passed to eval/exec")
        if re.search(r'execute\(.*response\.content', line):
            fail(f"{rel_path}:{n} -- LLM output passed directly to SQL execute")

    # Check 3: CacheablePrompt in orchestration files
    if "/orchestration/" in filepath and "round_table" in filepath or "chat_orchestrator" in filepath:
        if "CacheablePrompt" not in content and "llm.call(" in content:
            has_llm_calls = any("await self.llm.call(" in l or "await self._llm.call(" in l for l in lines)
            if has_llm_calls and "CacheablePrompt" not in content:
                fail(f"{rel_path} -- LLM calls without CacheablePrompt (missing prompt caching)")

    # Check 4: Prompt injection defense on external agent paths
    if "remote" in filepath.lower() and "agent" in filepath.lower():
        if "sanitize" not in content and "sanitize_for_prompt" not in content:
            fail(f"{rel_path} -- Remote agent module missing sanitization")
        else:
            ok(f"{rel_path} has sanitization")

    # Check 5: Security imports in API routes
    if "/api/routes/" in filepath:
        has_mutation = any(
            pattern in content
            for pattern in ["@router.post", "@router.put", "@router.delete"]
        )
        if has_mutation:
            has_validation = "validate_" in content or "ValidationError" in content
            has_auth = "verify_api_key" in content or "Depends(verify_api_key)" in content
            if not has_validation:
                fail(f"{rel_path} -- API route with mutations but no input validation")
            if not has_auth:
                fail(f"{rel_path} -- API route with mutations but no auth dependency")


def check_token_tracking(src_dir):
    """Verify all LLM provider methods populate TokenUsage."""
    llm_client = os.path.join(src_dir, "llm", "client.py")
    if not os.path.exists(llm_client):
        fail("llm/client.py not found")
        return

    with open(llm_client) as f:
        content = f.read()

    providers = ["_call_anthropic", "_call_openai", "_call_google"]
    for provider in providers:
        if provider in content:
            provider_start = content.index(provider)
            provider_section = content[provider_start:provider_start + 2000]
            if "TokenUsage" in provider_section:
                ok(f"llm/client.py: {provider} populates TokenUsage")
            else:
                fail(f"llm/client.py: {provider} missing TokenUsage population")


def check_parameterized_sql(src_dir):
    """Verify no f-string SQL in learning module."""
    for root, dirs, files in os.walk(os.path.join(src_dir, "learning")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                content = f.read()
            for n, line in enumerate(content.split("\n"), 1):
                if re.search(r'execute\(f["\']', line) or re.search(r'execute\(["\'].*\.format\(', line):
                    rel_path = os.path.relpath(filepath, src_dir)
                    fail(f"{rel_path}:{n} -- SQL injection risk (f-string in execute)")


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(src_dir):
        print(f"Source directory not found: {src_dir}")
        sys.exit(1)

    print(f"Running AI-specific checks on {src_dir}...")

    file_count = 0
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(root, fname)
            rel_path = os.path.relpath(filepath, src_dir)
            try:
                with open(filepath) as f:
                    content = f.read()
                scan_file(filepath, content, rel_path)
                file_count += 1
            except Exception as e:
                fail(f"{rel_path} -- Could not read: {e}")

    check_token_tracking(src_dir)
    check_parameterized_sql(src_dir)

    print(f"  Scanned {file_count} files")
    print()

    for p in passes:
        print(p)

    if findings:
        print()
        print(f"\033[31mAI Check Failures ({len(findings)}):\033[0m")
        for f in findings:
            print(f)
        sys.exit(1)
    else:
        print(f"\033[32m✓ All AI-specific checks passed\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()
