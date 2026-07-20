import unittest
from argparse import Namespace

from run_post_form_check import extract_preview_user_id, validate_args, validate_preview_target


class RunPostFormCheckTests(unittest.TestCase):
    def test_run_scout_requires_target_user_id(self):
        with self.assertRaisesRegex(SystemExit, "target-user-id"):
            validate_args(Namespace(run_scout=True, row=6, target_user_id="", request_delay="1"))

    def test_preview_only_does_not_require_target_user_id(self):
        validate_args(Namespace(run_scout=False, row=None, target_user_id="", request_delay="0"))

    def test_run_scout_accepts_target_user_id(self):
        validate_args(Namespace(run_scout=True, row=6, target_user_id="tom_brangus_cows_and_calves", request_delay="1"))

    def test_run_scout_requires_specific_row(self):
        with self.assertRaisesRegex(SystemExit, "row"):
            validate_args(
                Namespace(run_scout=True, row=None, target_user_id="tom_brangus_cows_and_calves", request_delay="1")
            )

    def test_run_scout_rejects_non_positive_request_delay(self):
        with self.assertRaisesRegex(SystemExit, "positive"):
            validate_args(
                Namespace(run_scout=True, row=6, target_user_id="tom_brangus_cows_and_calves", request_delay="0")
            )

    def test_preview_user_id_must_match_target(self):
        output = "Processing response\n  user_id will be: tom_brangus_cows_and_calves\n"

        self.assertEqual(extract_preview_user_id(output), "tom_brangus_cows_and_calves")
        validate_preview_target(output, "tom_brangus_cows_and_calves")
        with self.assertRaisesRegex(SystemExit, "does not match"):
            validate_preview_target(output, "another_user")


if __name__ == "__main__":
    unittest.main()
