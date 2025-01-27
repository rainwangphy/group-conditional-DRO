# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import contextlib
from io import StringIO
import logging
import os
import random
import tempfile
import unittest

import torch

from fairseq import options
from fairseq_cli import train
from fairseq_cli import eval_lm
from fairseq_cli import validate
from tests.utils import (
    create_dummy_data,
    preprocess_lm_data,
    preprocess_translation_data,
    train_translation_model,
    generate_main,
)


class TestTranslation(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_fconv(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_fconv") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(data_dir, "fconv_iwslt_de_en")
                generate_main(data_dir)

    def test_raw(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_fconv_raw") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir, ["--dataset-impl", "raw"])
                train_translation_model(
                    data_dir, "fconv_iwslt_de_en", ["--dataset-impl", "raw"]
                )
                generate_main(data_dir, ["--dataset-impl", "raw"])

    def test_update_freq(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_update_freq") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir, "fconv_iwslt_de_en", ["--update-freq", "3"]
                )
                generate_main(data_dir)

    def test_max_positions(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_max_positions") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                with self.assertRaises(Exception) as context:
                    train_translation_model(
                        data_dir,
                        "fconv_iwslt_de_en",
                        ["--max-target-positions", "5"],
                    )
                self.assertTrue(
                    "skip this example with --skip-invalid-size-inputs-valid-test"
                    in str(context.exception)
                )
                train_translation_model(
                    data_dir,
                    "fconv_iwslt_de_en",
                    [
                        "--max-target-positions",
                        "5",
                        "--skip-invalid-size-inputs-valid-test",
                    ],
                )
                with self.assertRaises(Exception) as context:
                    generate_main(data_dir)
                generate_main(data_dir, ["--skip-invalid-size-inputs-valid-test"])

    def test_generation(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_sampling") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(data_dir, "fconv_iwslt_de_en")
                generate_main(
                    data_dir,
                    [
                        "--sampling",
                        "--temperature",
                        "2",
                        "--beam",
                        "2",
                        "--nbest",
                        "2",
                    ],
                )
                generate_main(
                    data_dir,
                    [
                        "--sampling",
                        "--sampling-topk",
                        "3",
                        "--beam",
                        "2",
                        "--nbest",
                        "2",
                    ],
                )
                generate_main(
                    data_dir,
                    [
                        "--sampling",
                        "--sampling-topp",
                        "0.2",
                        "--beam",
                        "2",
                        "--nbest",
                        "2",
                    ],
                )
                generate_main(
                    data_dir,
                    [
                        "--diversity-rate",
                        "0.5",
                        "--beam",
                        "6",
                    ],
                )
                with self.assertRaises(ValueError):
                    generate_main(
                        data_dir,
                        [
                            "--diverse-beam-groups",
                            "4",
                            "--match-source-len",
                        ],
                    )
                generate_main(data_dir, ["--prefix-size", "2"])
                generate_main(data_dir, ["--retain-dropout"])

    def test_eval_bleu(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_eval_bleu") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "fconv_iwslt_de_en",
                    [
                        "--eval-bleu",
                        "--eval-bleu-print-samples",
                        "--eval-bleu-remove-bpe",
                        "--eval-bleu-detok",
                        "space",
                        "--eval-bleu-args",
                        '{"beam": 4, "min_len": 10}',
                    ],
                )

    def test_lstm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lstm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "lstm_wiseman_iwslt_de_en",
                    [
                        "--encoder-layers",
                        "2",
                        "--decoder-layers",
                        "2",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                        "--decoder-out-embed-dim",
                        "8",
                    ],
                )
                generate_main(data_dir)

    def test_lstm_bidirectional(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lstm_bidirectional") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "lstm",
                    [
                        "--encoder-layers",
                        "2",
                        "--encoder-bidirectional",
                        "--encoder-hidden-size",
                        "16",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                        "--decoder-out-embed-dim",
                        "8",
                        "--decoder-layers",
                        "2",
                    ],
                )
                generate_main(data_dir)

    def test_transformer(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_transformer") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "transformer_iwslt_de_en",
                    [
                        "--encoder-layers",
                        "2",
                        "--decoder-layers",
                        "2",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                    ],
                    run_validation=True,
                )
                generate_main(data_dir)

    def test_multilingual_transformer(self):
        # test with all combinations of encoder/decoder lang tokens
        encoder_langtok_flags = [
            [],
            ["--encoder-langtok", "src"],
            ["--encoder-langtok", "tgt"],
        ]
        decoder_langtok_flags = [[], ["--decoder-langtok"]]
        with contextlib.redirect_stdout(StringIO()):
            for i in range(len(encoder_langtok_flags)):
                for j in range(len(decoder_langtok_flags)):
                    enc_ltok_flag = encoder_langtok_flags[i]
                    dec_ltok_flag = decoder_langtok_flags[j]
                    with tempfile.TemporaryDirectory(
                        f"test_multilingual_transformer_{i}_{j}"
                    ) as data_dir:
                        create_dummy_data(data_dir)
                        preprocess_translation_data(data_dir)
                        train_translation_model(
                            data_dir,
                            arch="multilingual_transformer",
                            task="multilingual_translation",
                            extra_flags=[
                                "--encoder-layers",
                                "2",
                                "--decoder-layers",
                                "2",
                                "--encoder-embed-dim",
                                "8",
                                "--decoder-embed-dim",
                                "8",
                            ]
                            + enc_ltok_flag
                            + dec_ltok_flag,
                            lang_flags=["--lang-pairs", "in-out,out-in"],
                            run_validation=True,
                            extra_valid_flags=enc_ltok_flag + dec_ltok_flag,
                        )
                        generate_main(
                            data_dir,
                            extra_flags=[
                                "--task",
                                "multilingual_translation",
                                "--lang-pairs",
                                "in-out,out-in",
                                "--source-lang",
                                "in",
                                "--target-lang",
                                "out",
                            ]
                            + enc_ltok_flag
                            + dec_ltok_flag,
                        )

    def test_translation_multi_simple_epoch(self):
        # test with all combinations of encoder/decoder lang tokens
        encoder_langtok_flags = [
            [],
            ["--encoder-langtok", "src"],
            ["--encoder-langtok", "tgt"],
        ]
        decoder_langtok_flags = [[], ["--decoder-langtok"]]
        with contextlib.redirect_stdout(StringIO()):
            for i in range(len(encoder_langtok_flags)):
                for j in range(len(decoder_langtok_flags)):
                    enc_ltok_flag = encoder_langtok_flags[i]
                    dec_ltok_flag = decoder_langtok_flags[j]
                    with tempfile.TemporaryDirectory(
                        f"test_translation_multi_simple_epoch_{i}_{j}"
                    ) as data_dir:
                        create_dummy_data(data_dir)
                        preprocess_translation_data(data_dir)
                        train_translation_model(
                            data_dir,
                            arch="transformer",
                            task="translation_multi_simple_epoch",
                            extra_flags=[
                                "--encoder-layers",
                                "2",
                                "--decoder-layers",
                                "2",
                                "--encoder-embed-dim",
                                "8",
                                "--decoder-embed-dim",
                                "8",
                                "--sampling-method",
                                "temperature",
                                "--sampling-temperature",
                                "1.5",
                                "--virtual-epoch-size",
                                "1000",
                            ]
                            + enc_ltok_flag
                            + dec_ltok_flag,
                            lang_flags=["--lang-pairs", "in-out,out-in"],
                            run_validation=True,
                            extra_valid_flags=enc_ltok_flag + dec_ltok_flag,
                        )
                        generate_main(
                            data_dir,
                            extra_flags=[
                                "--task",
                                "translation_multi_simple_epoch",
                                "--lang-pairs",
                                "in-out,out-in",
                                "--source-lang",
                                "in",
                                "--target-lang",
                                "out",
                            ]
                            + enc_ltok_flag
                            + dec_ltok_flag,
                        )

    def test_transformer_cross_self_attention(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory(
                "test_transformer_cross_self_attention"
            ) as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "transformer_iwslt_de_en",
                    [
                        "--encoder-layers",
                        "2",
                        "--decoder-layers",
                        "2",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                        "--no-cross-attention",
                        "--cross-self-attention",
                    ],
                    run_validation=True,
                )
                generate_main(data_dir, extra_flags=[])

    def test_lightconv(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lightconv") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "lightconv_iwslt_de_en",
                    [
                        "--encoder-conv-type",
                        "lightweight",
                        "--decoder-conv-type",
                        "lightweight",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                    ],
                )
                generate_main(data_dir)

    def test_dynamicconv(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_dynamicconv") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "lightconv_iwslt_de_en",
                    [
                        "--encoder-conv-type",
                        "dynamic",
                        "--decoder-conv-type",
                        "dynamic",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                    ],
                )
                generate_main(data_dir)

    def test_cmlm_transformer(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_cmlm_transformer") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir, ["--joined-dictionary"])
                train_translation_model(
                    data_dir,
                    "cmlm_transformer",
                    [
                        "--apply-bert-init",
                        "--criterion",
                        "nat_loss",
                        "--noise",
                        "full_mask",
                        "--pred-length-offset",
                        "--length-loss-factor",
                        "0.1",
                    ],
                    task="translation_lev",
                )
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "translation_lev",
                        "--iter-decode-max-iter",
                        "9",
                        "--iter-decode-eos-penalty",
                        "0",
                        "--print-step",
                    ],
                )

    def test_nonautoregressive_transformer(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory(
                "test_nonautoregressive_transformer"
            ) as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir, ["--joined-dictionary"])
                train_translation_model(
                    data_dir,
                    "nonautoregressive_transformer",
                    [
                        "--apply-bert-init",
                        "--src-embedding-copy",
                        "--criterion",
                        "nat_loss",
                        "--noise",
                        "full_mask",
                        "--pred-length-offset",
                        "--length-loss-factor",
                        "0.1",
                    ],
                    task="translation_lev",
                )
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "translation_lev",
                        "--iter-decode-max-iter",
                        "0",
                        "--iter-decode-eos-penalty",
                        "0",
                        "--print-step",
                    ],
                )

    # def test_nat_crf_transformer(self):
    #     with contextlib.redirect_stdout(StringIO()):
    #         with tempfile.TemporaryDirectory('test_nat_crf_transformer') as data_dir:
    #             create_dummy_data(data_dir)
    #             preprocess_translation_data(data_dir, ['--joined-dictionary'])
    #             train_translation_model(data_dir, 'nacrf_transformer', [
    #                 '--apply-bert-init', '--criterion',
    #                 'nat_loss', '--noise', 'full_mask', '--pred-length-offset',
    #                 '--length-loss-factor', '0.1',
    #                 '--word-ins-loss-factor', '0.5',
    #                 '--crf-lowrank-approx', '1',
    #                 '--crf-beam-approx', '1'
    #             ], task='translation_lev')
    #             generate_main(data_dir, [
    #                 '--task', 'translation_lev',
    #                 '--iter-decode-max-iter', '0',
    #                 '--iter-decode-eos-penalty', '0',
    #                 '--print-step',
    #             ])

    def test_iterative_nonautoregressive_transformer(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory(
                "test_iterative_nonautoregressive_transformer"
            ) as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir, ["--joined-dictionary"])
                train_translation_model(
                    data_dir,
                    "iterative_nonautoregressive_transformer",
                    [
                        "--apply-bert-init",
                        "--src-embedding-copy",
                        "--criterion",
                        "nat_loss",
                        "--noise",
                        "full_mask",
                        "--stochastic-approx",
                        "--dae-ratio",
                        "0.5",
                        "--train-step",
                        "3",
                    ],
                    task="translation_lev",
                )
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "translation_lev",
                        "--iter-decode-max-iter",
                        "9",
                        "--iter-decode-eos-penalty",
                        "0",
                        "--print-step",
                    ],
                )

    def test_insertion_transformer(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_insertion_transformer") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir, ["--joined-dictionary"])
                train_translation_model(
                    data_dir,
                    "insertion_transformer",
                    [
                        "--apply-bert-init",
                        "--criterion",
                        "nat_loss",
                        "--noise",
                        "random_mask",
                    ],
                    task="translation_lev",
                )
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "translation_lev",
                        "--iter-decode-max-iter",
                        "9",
                        "--iter-decode-eos-penalty",
                        "0",
                        "--print-step",
                    ],
                )

    def test_mixture_of_experts(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_moe") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                train_translation_model(
                    data_dir,
                    "transformer_iwslt_de_en",
                    [
                        "--task",
                        "translation_moe",
                        "--user-dir",
                        "examples/translation_moe/src",
                        "--method",
                        "hMoElp",
                        "--mean-pool-gating-network",
                        "--num-experts",
                        "3",
                        "--encoder-layers",
                        "2",
                        "--decoder-layers",
                        "2",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                    ],
                )
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "translation_moe",
                        "--user-dir",
                        "examples/translation_moe/src",
                        "--method",
                        "hMoElp",
                        "--mean-pool-gating-network",
                        "--num-experts",
                        "3",
                        "--gen-expert",
                        "0",
                    ],
                )

    def test_alignment(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_alignment") as data_dir:
                create_dummy_data(data_dir, alignment=True)
                preprocess_translation_data(data_dir, ["--align-suffix", "align"])
                train_translation_model(
                    data_dir,
                    "transformer_align",
                    [
                        "--encoder-layers",
                        "2",
                        "--decoder-layers",
                        "2",
                        "--encoder-embed-dim",
                        "8",
                        "--decoder-embed-dim",
                        "8",
                        "--load-alignments",
                        "--alignment-layer",
                        "1",
                        "--criterion",
                        "label_smoothed_cross_entropy_with_alignment",
                    ],
                    run_validation=True,
                )
                generate_main(data_dir)


class TestStories(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_fconv_self_att_wp(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_fconv_self_att_wp") as data_dir:
                create_dummy_data(data_dir)
                preprocess_translation_data(data_dir)
                config = [
                    "--encoder-layers",
                    "[(128, 3)] * 2",
                    "--decoder-layers",
                    "[(128, 3)] * 2",
                    "--decoder-attention",
                    "True",
                    "--encoder-attention",
                    "False",
                    "--gated-attention",
                    "True",
                    "--self-attention",
                    "True",
                    "--project-input",
                    "True",
                    "--encoder-embed-dim",
                    "8",
                    "--decoder-embed-dim",
                    "8",
                    "--decoder-out-embed-dim",
                    "8",
                    "--multihead-self-attention-nheads",
                    "2",
                ]
                train_translation_model(data_dir, "fconv_self_att_wp", config)
                generate_main(data_dir)

                # fusion model
                os.rename(
                    os.path.join(data_dir, "checkpoint_last.pt"),
                    os.path.join(data_dir, "pretrained.pt"),
                )
                config.extend(
                    [
                        "--pretrained",
                        "True",
                        "--pretrained-checkpoint",
                        os.path.join(data_dir, "pretrained.pt"),
                        "--save-dir",
                        os.path.join(data_dir, "fusion_model"),
                    ]
                )
                train_translation_model(data_dir, "fconv_self_att_wp", config)


class TestLanguageModeling(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_fconv_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_fconv_lm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_language_model(
                    data_dir,
                    "fconv_lm",
                    [
                        "--decoder-layers",
                        "[(850, 3)] * 2 + [(1024,4)]",
                        "--decoder-embed-dim",
                        "280",
                        "--optimizer",
                        "nag",
                        "--lr",
                        "0.1",
                    ],
                )
                eval_lm_main(data_dir)
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "language_modeling",
                        "--sample-break-mode",
                        "eos",
                        "--tokens-per-sample",
                        "500",
                    ],
                )

    def test_transformer_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_transformer_lm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_language_model(
                    data_dir,
                    "transformer_lm",
                    ["--add-bos-token"],
                    run_validation=True,
                )
                eval_lm_main(data_dir)
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "language_modeling",
                        "--sample-break-mode",
                        "eos",
                        "--tokens-per-sample",
                        "500",
                    ],
                )

    def test_lightconv_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lightconv_lm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_language_model(
                    data_dir,
                    "lightconv_lm",
                    ["--add-bos-token"],
                    run_validation=True,
                )
                eval_lm_main(data_dir)
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "language_modeling",
                        "--sample-break-mode",
                        "eos",
                        "--tokens-per-sample",
                        "500",
                    ],
                )

    def test_lstm_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lstm_lm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_language_model(
                    data_dir,
                    "lstm_lm",
                    ["--add-bos-token"],
                    run_validation=True,
                )
                eval_lm_main(data_dir)
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "language_modeling",
                        "--sample-break-mode",
                        "eos",
                        "--tokens-per-sample",
                        "500",
                    ],
                )

    def test_lstm_lm_residuals(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_lstm_lm_residuals") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_language_model(
                    data_dir,
                    "lstm_lm",
                    ["--add-bos-token", "--residuals"],
                    run_validation=True,
                )
                eval_lm_main(data_dir)
                generate_main(
                    data_dir,
                    [
                        "--task",
                        "language_modeling",
                        "--sample-break-mode",
                        "eos",
                        "--tokens-per-sample",
                        "500",
                    ],
                )


class TestMaskedLanguageModel(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_legacy_masked_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_legacy_mlm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_legacy_masked_language_model(data_dir, "masked_lm")

    def test_roberta_masked_lm(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_roberta_mlm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_masked_lm(data_dir, "roberta_base")

    def test_roberta_sentence_prediction(self):
        num_classes = 3
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_roberta_head") as data_dir:
                create_dummy_roberta_head_data(data_dir, num_classes=num_classes)
                preprocess_lm_data(os.path.join(data_dir, "input0"))
                preprocess_lm_data(os.path.join(data_dir, "label"))
                train_roberta_head(data_dir, "roberta_base", num_classes=num_classes)

    def test_roberta_regression_single(self):
        num_classes = 1
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory(
                "test_roberta_regression_single"
            ) as data_dir:
                create_dummy_roberta_head_data(
                    data_dir, num_classes=num_classes, regression=True
                )
                preprocess_lm_data(os.path.join(data_dir, "input0"))
                train_roberta_head(
                    data_dir,
                    "roberta_base",
                    num_classes=num_classes,
                    extra_flags=["--regression-target"],
                )

    def test_roberta_regression_multiple(self):
        num_classes = 3
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory(
                "test_roberta_regression_multiple"
            ) as data_dir:
                create_dummy_roberta_head_data(
                    data_dir, num_classes=num_classes, regression=True
                )
                preprocess_lm_data(os.path.join(data_dir, "input0"))
                train_roberta_head(
                    data_dir,
                    "roberta_base",
                    num_classes=num_classes,
                    extra_flags=["--regression-target"],
                )

    def _test_pretrained_masked_lm_for_translation(self, learned_pos_emb, encoder_only):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_mlm") as data_dir:
                create_dummy_data(data_dir)
                preprocess_lm_data(data_dir)
                train_legacy_masked_language_model(
                    data_dir,
                    arch="masked_lm",
                    extra_args=("--encoder-learned-pos",) if learned_pos_emb else (),
                )
                with tempfile.TemporaryDirectory(
                    "test_mlm_translation"
                ) as translation_dir:
                    create_dummy_data(translation_dir)
                    preprocess_translation_data(
                        translation_dir, extra_flags=["--joined-dictionary"]
                    )
                    # Train transformer with data_dir/checkpoint_last.pt
                    train_translation_model(
                        translation_dir,
                        arch="transformer_from_pretrained_xlm",
                        extra_flags=[
                            "--decoder-layers",
                            "1",
                            "--decoder-embed-dim",
                            "32",
                            "--decoder-attention-heads",
                            "1",
                            "--decoder-ffn-embed-dim",
                            "32",
                            "--encoder-layers",
                            "1",
                            "--encoder-embed-dim",
                            "32",
                            "--encoder-attention-heads",
                            "1",
                            "--encoder-ffn-embed-dim",
                            "32",
                            "--pretrained-xlm-checkpoint",
                            "{}/checkpoint_last.pt".format(data_dir),
                            "--activation-fn",
                            "gelu",
                            "--max-source-positions",
                            "500",
                            "--max-target-positions",
                            "500",
                        ]
                        + (
                            ["--encoder-learned-pos", "--decoder-learned-pos"]
                            if learned_pos_emb
                            else []
                        )
                        + (["--init-encoder-only"] if encoder_only else []),
                        task="translation_from_pretrained_xlm",
                    )

    def test_pretrained_masked_lm_for_translation_learned_pos_emb(self):
        self._test_pretrained_masked_lm_for_translation(True, False)

    def test_pretrained_masked_lm_for_translation_sinusoidal_pos_emb(self):
        self._test_pretrained_masked_lm_for_translation(False, False)

    def test_pretrained_masked_lm_for_translation_encoder_only(self):
        self._test_pretrained_masked_lm_for_translation(True, True)


def train_legacy_masked_language_model(data_dir, arch, extra_args=()):
    train_parser = options.get_training_parser()
    # TODO: langs should be in and out right?
    train_args = options.parse_args_and_arch(
        train_parser,
        [
            "--task",
            "cross_lingual_lm",
            data_dir,
            "--arch",
            arch,
            # Optimizer args
            "--optimizer",
            "adam",
            "--lr-scheduler",
            "reduce_lr_on_plateau",
            "--lr-shrink",
            "0.5",
            "--lr",
            "0.0001",
            "--min-lr",
            "1e-09",
            # dropout, attention args
            "--dropout",
            "0.1",
            "--attention-dropout",
            "0.1",
            # MLM args
            "--criterion",
            "legacy_masked_lm_loss",
            "--masked-lm-only",
            "--monolingual-langs",
            "in,out",
            "--num-segment",
            "5",
            # Transformer args: use a small transformer model for fast training
            "--encoder-layers",
            "1",
            "--encoder-embed-dim",
            "32",
            "--encoder-attention-heads",
            "1",
            "--encoder-ffn-embed-dim",
            "32",
            # Other training args
            "--max-tokens",
            "500",
            "--tokens-per-sample",
            "500",
            "--save-dir",
            data_dir,
            "--max-epoch",
            "1",
            "--no-progress-bar",
            "--distributed-world-size",
            "1",
            "--dataset-impl",
            "raw",
        ]
        + list(extra_args),
    )
    train.main(train_args)


class TestOptimizers(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_optimizers(self):
        with contextlib.redirect_stdout(StringIO()):
            with tempfile.TemporaryDirectory("test_optimizers") as data_dir:
                # Use just a bit of data and tiny model to keep this test runtime reasonable
                create_dummy_data(data_dir, num_examples=10, maxlen=5)
                preprocess_translation_data(data_dir)
                optimizers = ["adafactor", "adam", "nag", "adagrad", "sgd", "adadelta"]
                last_checkpoint = os.path.join(data_dir, "checkpoint_last.pt")
                for optimizer in optimizers:
                    if os.path.exists(last_checkpoint):
                        os.remove(last_checkpoint)
                    train_translation_model(
                        data_dir,
                        "lstm",
                        [
                            "--required-batch-size-multiple",
                            "1",
                            "--encoder-layers",
                            "1",
                            "--encoder-hidden-size",
                            "32",
                            "--decoder-layers",
                            "1",
                            "--optimizer",
                            optimizer,
                        ],
                    )
                    generate_main(data_dir)


def create_dummy_roberta_head_data(
    data_dir, num_examples=100, maxlen=10, num_classes=2, regression=False
):
    input_dir = "input0"

    def _create_dummy_data(filename):
        random_data = torch.rand(num_examples * maxlen)
        input_data = 97 + torch.floor(26 * random_data).int()
        if regression:
            output_data = torch.rand((num_examples, num_classes))
        else:
            output_data = 1 + torch.floor(num_classes * torch.rand(num_examples)).int()
        with open(os.path.join(data_dir, input_dir, filename + ".out"), "w") as f_in:
            label_filename = filename + ".label" if regression else filename + ".out"
            with open(os.path.join(data_dir, "label", label_filename), "w") as f_out:
                offset = 0
                for i in range(num_examples):
                    # write example input
                    ex_len = random.randint(1, maxlen)
                    ex_str = " ".join(map(chr, input_data[offset : offset + ex_len]))
                    print(ex_str, file=f_in)
                    # write example label
                    if regression:
                        class_str = " ".join(map(str, output_data[i].numpy()))
                        print(class_str, file=f_out)
                    else:
                        class_str = "class{}".format(output_data[i])
                        print(class_str, file=f_out)
                    offset += ex_len

    os.mkdir(os.path.join(data_dir, input_dir))
    os.mkdir(os.path.join(data_dir, "label"))
    _create_dummy_data("train")
    _create_dummy_data("valid")
    _create_dummy_data("test")


def train_masked_lm(data_dir, arch, extra_flags=None):
    train_parser = options.get_training_parser()
    train_args = options.parse_args_and_arch(
        train_parser,
        [
            "--task",
            "masked_lm",
            data_dir,
            "--arch",
            arch,
            "--optimizer",
            "adam",
            "--lr",
            "0.0001",
            "--criterion",
            "masked_lm",
            "--max-sentences",
            "500",
            "--save-dir",
            data_dir,
            "--max-epoch",
            "1",
            "--no-progress-bar",
            "--distributed-world-size",
            "1",
            "--ddp-backend",
            "no_c10d",
            "--num-workers",
            0,
        ]
        + (extra_flags or []),
    )
    train.main(train_args)


def train_roberta_head(data_dir, arch, num_classes=2, extra_flags=None):
    train_parser = options.get_training_parser()
    train_args = options.parse_args_and_arch(
        train_parser,
        [
            "--task",
            "sentence_prediction",
            data_dir,
            "--arch",
            arch,
            "--num-classes",
            str(num_classes),
            "--optimizer",
            "adam",
            "--lr",
            "0.0001",
            "--criterion",
            "sentence_prediction",
            "--max-tokens",
            "500",
            "--max-positions",
            "500",
            "--max-sentences",
            "500",
            "--save-dir",
            data_dir,
            "--max-epoch",
            "1",
            "--no-progress-bar",
            "--distributed-world-size",
            "1",
            "--ddp-backend",
            "no_c10d",
            "--num-workers",
            0,
        ]
        + (extra_flags or []),
    )
    train.main(train_args)


def train_language_model(data_dir, arch, extra_flags=None, run_validation=False):
    train_parser = options.get_training_parser()
    train_args = options.parse_args_and_arch(
        train_parser,
        [
            "--task",
            "language_modeling",
            data_dir,
            "--arch",
            arch,
            "--optimizer",
            "adam",
            "--lr",
            "0.0001",
            "--criterion",
            "adaptive_loss",
            "--adaptive-softmax-cutoff",
            "5,10,15",
            "--max-tokens",
            "500",
            "--tokens-per-sample",
            "500",
            "--save-dir",
            data_dir,
            "--max-epoch",
            "1",
            "--no-progress-bar",
            "--distributed-world-size",
            "1",
            "--ddp-backend",
            "no_c10d",
        ]
        + (extra_flags or []),
    )
    train.main(train_args)

    if run_validation:
        # test validation
        validate_parser = options.get_validation_parser()
        validate_args = options.parse_args_and_arch(
            validate_parser,
            [
                "--task",
                "language_modeling",
                data_dir,
                "--path",
                os.path.join(data_dir, "checkpoint_last.pt"),
                "--valid-subset",
                "valid",
                "--max-tokens",
                "500",
                "--no-progress-bar",
            ],
        )
        validate.main(validate_args)


def eval_lm_main(data_dir):
    eval_lm_parser = options.get_eval_lm_parser()
    eval_lm_args = options.parse_args_and_arch(
        eval_lm_parser,
        [
            data_dir,
            "--path",
            os.path.join(data_dir, "checkpoint_last.pt"),
            "--no-progress-bar",
        ],
    )
    eval_lm.main(eval_lm_args)


def train_masked_language_model(data_dir, arch, extra_args=()):
    train_parser = options.get_training_parser()
    # TODO: langs should be in and out right?
    train_args = options.parse_args_and_arch(
        train_parser,
        [
            "--task",
            "cross_lingual_lm",
            data_dir,
            "--arch",
            arch,
            # Optimizer args
            "--optimizer",
            "adam",
            "--lr-scheduler",
            "reduce_lr_on_plateau",
            "--lr-shrink",
            "0.5",
            "--lr",
            "0.0001",
            "--min-lr",
            "1e-09",
            # dropout, attention args
            "--dropout",
            "0.1",
            "--attention-dropout",
            "0.1",
            # MLM args
            "--criterion",
            "masked_lm_loss",
            "--masked-lm-only",
            "--monolingual-langs",
            "in,out",
            "--num-segment",
            "5",
            # Transformer args: use a small transformer model for fast training
            "--encoder-layers",
            "1",
            "--encoder-embed-dim",
            "32",
            "--encoder-attention-heads",
            "1",
            "--encoder-ffn-embed-dim",
            "32",
            # Other training args
            "--max-tokens",
            "500",
            "--tokens-per-sample",
            "500",
            "--save-dir",
            data_dir,
            "--max-epoch",
            "1",
            "--no-progress-bar",
            "--distributed-world-size",
            "1",
            "--dataset-impl",
            "raw",
        ]
        + list(extra_args),
    )
    train.main(train_args)


if __name__ == "__main__":
    unittest.main()
