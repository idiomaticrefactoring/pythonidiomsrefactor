# -*- coding: utf-8 -*-
"""
RIdiom - Python Code Refactoring Tool

Main entry point for the refactoring/explaining tool.
Uses the new ridiom_core architecture with unified rule registry.
"""

import argparse
import os
import fnmatch
from typing import List, Dict

# Import the new core infrastructure
from ridiom_core import (
    RuleRegistry,
    Config,
    load_config,
    load_file_path,
    save_json_file_path,
    RuleResult,
    CodeInfo,
)
from ridiom_core.config import set_config
import ridiom_core.rules  # Trigger rule registration


# ==========================================
# Helper Functions
# ==========================================


def check_noqa(file_lines: List[str], lineno_list: List[List[int]]) -> bool:
    """Check if any line in the range contains '# noqa'."""
    if not file_lines:
        return False

    for start, end in lineno_list:
        start_idx = max(0, start - 1)
        end_idx = min(len(file_lines), end)

        for i in range(start_idx, end_idx):
            if "# noqa" in file_lines[i]:
                return True
    return False


def get_target_files(base_paths: List[str], exclude_patterns: List[str]) -> List[str]:
    """Scan for Python files based on include/exclude patterns."""
    target_files = []

    for base_path in base_paths:
        if base_path == ".":
            base_path = os.getcwd()

        if os.path.isfile(base_path):
            target_files.append(base_path)
            continue

        for root, dirs, files in os.walk(base_path):
            # Filter directories
            dirs[:] = [
                d
                for d in dirs
                if not any(fnmatch.fnmatch(d, pat) for pat in exclude_patterns)
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, os.getcwd())

                # Filter files
                if any(
                    fnmatch.fnmatch(relpath, pat) or fnmatch.fnmatch(file, pat)
                    for pat in exclude_patterns
                ):
                    continue

                target_files.append(filepath)

    return target_files


# ==========================================
# Core Processing Logic
# ==========================================


def process_file(
    filepath: str,
    config: Config,
    mode: str,
) -> List[Dict]:
    """
    Process a single file with all active rules.

    Returns:
        List of result dictionaries for this file.
    """
    print(
        f"************ [{mode.title()}] Processing {os.path.basename(filepath)} ************"
    )

    file_results_output: List[Dict] = []

    # Load file content
    try:
        content = load_file_path(filepath)
    except Exception as e:
        print(f"Failed to load {filepath}: {e}")
        return file_results_output

    # Read source lines for noqa checking
    file_lines = []
    if config.enable_noqa:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_lines = f.readlines()
        except Exception as e:
            print(f"⚠️  Warning: Cannot read {filepath} for noqa check: {e}")

    file_results: List[RuleResult] = []

    # Get active rules for this mode
    active_rules = RuleRegistry.all_instances(mode)

    for rule in active_rules:
        # Check if rule is enabled in config
        if not config.is_rule_enabled(rule.name):
            continue

        # Get rule-specific config and add mode indicator
        rule_config = config.get_rule_config(rule.name).copy()
        rule_config["_mode"] = mode

        try:
            results = rule.match(content, config=rule_config)

            if results:
                # Filter out noqa-marked results
                if config.enable_noqa and file_lines:
                    valid_results = []
                    for res in results:
                        if not check_noqa(file_lines, res.lineno):
                            valid_results.append(res)
                    file_results.extend(valid_results)
                else:
                    file_results.extend(results)

        except Exception as e:
            import traceback

            print(f"Error executing rule '{rule.name}' on {filepath}: {e}")
            traceback.print_exc()

    # Output results
    if file_results:
        print(
            f"************ Result Summary of {os.path.basename(filepath)} ************"
        )

        for ind, res in enumerate(file_results):
            code_info = CodeInfo(
                file_path=filepath,
                idiom=res.idiom_name,
                class_name=res.class_name,
                method_name=res.method_name,
                old_code=res.old_code,
                new_code=res.new_code,
                lineno=res.lineno,
            )
            print(f">>> Result {ind + 1} \n{code_info.full_info()}")
            file_results_output.append(code_info.__dict__)

        print(f"************ End of {os.path.basename(filepath)} ************\n")

    return file_results_output


# ==========================================
# Main Entry Point
# ==========================================


def main():
    parser = argparse.ArgumentParser(
        description="RIdiom: Detect and refactor/explain Python code."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="ridiom.toml",
        help="Path to ridiom.toml config file",
    )
    parser.add_argument(
        "--filepath",
        type=str,
        help="Override target path (file or directory)",
    )
    parser.add_argument(
        "--outputpath",
        type=str,
        help="Override output path (if specified, all results go to this single file)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["refactor", "explain"],
        help="Operation mode: 'refactor' (default) or 'explain'",
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    set_config(config)

    # Determine mode: CLI args > Config > Default
    mode = args.mode if args.mode else config.mode
    print(f"Operation Mode: {mode}")

    # Print registered rules for debugging
    print(f"Registered rules: {RuleRegistry.names()}")

    # Scan for files
    include_paths = [args.filepath] if args.filepath else config.include
    target_files = get_target_files(include_paths, config.exclude)
    print(f"Found {len(target_files)} python files to analyze.")

    # Check active rules
    active_rules = [r for r in RuleRegistry.all(mode) if config.is_rule_enabled(r.name)]
    if not active_rules:
        print("No active rules selected. Exiting.")
        return

    print(f"Active rules: {[r.name for r in active_rules]}")

    # Process files and save results
    if args.outputpath:
        # User specified output path: collect all results into single file
        all_results = []
        for filepath in target_files:
            file_results = process_file(filepath, config, mode)
            all_results.extend(file_results)

        if all_results:
            save_json_file_path(args.outputpath, all_results)
            print(f"Results saved to {args.outputpath}")
    else:
        # Default: save results per file in same directory
        for filepath in target_files:
            file_results = process_file(filepath, config, mode)

            if file_results:
                # Generate output path: same directory as source file
                # Format: filename_mode_output_file
                file_dir = os.path.dirname(os.path.abspath(filepath))
                file_basename = os.path.splitext(os.path.basename(filepath))[0]
                output_filename = f"{file_basename}_{mode}_{config.output_file}"
                output_path = os.path.join(file_dir, output_filename)

                save_json_file_path(output_path, file_results)
                print(f"Results saved to {output_path}")

    print("Analysis finished!")


if __name__ == "__main__":
    main()
