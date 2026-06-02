import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

import json
from pathlib import Path

from app.services.agent_service import run_agents


BASE_DIR = Path(__file__).parent

TEST_FOLDERS = [
    "business",
    "meetings",
    "research",
    "mixed"
]


def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_expected(test_name):
    expected_file = (
        BASE_DIR
        / "expected"
        / f"{test_name}.json"
    )

    if not expected_file.exists():
        return None

    with open(expected_file, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_agents(actual, expected):

    actual_agents = set(
        actual["plan"]["selected_agents"]
    )

    expected_agents = set(
        expected.get("agents", [])
    )

    return actual_agents == expected_agents


def run_test_case(test_file):

    test_name = test_file.stem

    print("=" * 60)
    print(f"TEST: {test_name}")

    text = load_text(test_file)

    result = run_agents(
        text=text,
        summary_length="short"
    )

    expected = load_expected(test_name)

    if expected is None:
        print("⚠ No expected file found")
        return False

    passed = True

    # Agent validation
    if compare_agents(result, expected):
        print("✅ Agent Selection")
    else:
        print("❌ Agent Selection")

        print(
            "Expected:",
            expected.get("agents")
        )

        print(
            "Actual:",
            result["plan"]["selected_agents"]
        )

        passed = False

    print(
        "Selected Agents:",
        result["plan"]["selected_agents"]
    )

    print(
        "Execution:",
        result["execution"]
    )

    return passed


def main():

    total = 0
    passed = 0

    for folder in TEST_FOLDERS:

        folder_path = BASE_DIR / folder

        if not folder_path.exists():
            continue

        for file in folder_path.glob("*.txt"):

            total += 1

            if run_test_case(file):
                passed += 1

    print("\n")
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    print(f"Passed: {passed}")
    print(f"Total : {total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED")
    else:
        print("⚠ SOME TESTS FAILED")


if __name__ == "__main__":
    main()