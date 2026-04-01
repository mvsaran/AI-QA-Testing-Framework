from aiqa_testing.datasets import load_test_cases


def test_dataset_contains_cases(settings):
    cases = load_test_cases(settings.dataset_path)
    assert cases, "Expected at least one test case in the dataset."


def test_dataset_case_ids_are_unique(settings):
    cases = load_test_cases(settings.dataset_path)
    case_ids = [case.case_id for case in cases]
    assert len(case_ids) == len(set(case_ids)), "Dataset contains duplicate case ids."
