# -*- coding: utf-8 -*-
"""
    This module is intended to join all the pipeline in separated tasks
    to be executed individually or in a flow by using command-line options

    Example:
    Dataset embedding and processing:
        $ python taskflows.py -e -pS
"""


import argparse
import gc
import os
import shutil
import subprocess
from argparse import ArgumentParser

import pandas as pd
from gensim.models.word2vec import Word2Vec

import configs
import src.data as data
import src.prepare as prepare
import src.process as process
import src.utils.functions.cpg as cpg

PATHS = configs.PathsConfig()
FILES = configs.FilesConfig()
DEVICE = FILES.get_device()


def c_project_filter_func(dataset: pd.DataFrame) -> pd.DataFrame:
    # ["FFmpeg", "qemu"]
    result: pd.DataFrame = dataset.loc[dataset["project"] == "FFmpeg"]

    len_filter = result.func.str.len() < 1_000
    result = result.loc[len_filter]

    result = result.head(200)

    return result


def create_cpg_json():
    create_config = configs.CreateConfig()
    json_file = (
        "dataset.json" if create_config.language == "csharp" else "dataset.c.json"
    )
    raw = data.read(PATHS.raw, json_file)
    filter_func = None if create_config.language == "csharp" else None
    # c_project_filter_func
    filtered = data.apply_filter(raw, filter_func)
    filtered = data.clean(filtered)
    data.drop(filtered, ["commit_id"])
    slices = data.slice_frame(filtered, create_config.slice_size)
    slices = [(s, slice.apply(lambda x: x)) for s, slice in slices]

    cpg_files: list[str] = []
    log_file_path = os.path.join(PATHS.cpg, "joern_parse.log")

    # Delete log file if it exists
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print(f"Deleted old log file: {log_file_path}")

    # Create CPG binary files
    for s, slice in slices:
        data.to_files(slice, PATHS.joern, create_config.language)

        cpg_file = prepare.joern_parse(
            create_config, PATHS.joern, PATHS.cpg, f"{s}_{FILES.cpg}.bin"
        )
        print(f"Dataset {s} to cpg.")
        shutil.rmtree(PATHS.joern)

        # joern create
        joern_repl_binary = os.path.join(
            os.getcwd(),
            create_config.joern_cli_dir,
            "joern",
        )

        # TODO: fix "cpg_file.split('.')[0]" to be more robust
        json_file = f"{cpg_file.split('.')[0]}.json"
        cpg_file_path = os.path.join(os.getcwd(), PATHS.cpg, cpg_file)

        if not os.path.exists(cpg_file_path):
            continue

        cpg_file_path = f"{os.path.abspath(PATHS.cpg)}/{cpg_file}"
        json_file_path = f"{os.path.abspath(PATHS.cpg)}/{json_file}"
        script_path = f"{os.path.dirname(os.path.abspath(create_config.joern_cli_dir))}/graph-for-funcs.sc"

        cmd = " ".join(
            [
                joern_repl_binary,
                "-J-Xmx25G",
                f"--script {script_path}",
                f"--param cpgFile={cpg_file_path}",
                f"--param outFile={json_file_path}",
            ]
        )

        try:
            subprocess.run(
                cmd,
                text=True,
                check=True,
                shell=True,
                cwd=os.getcwd(),
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            print(f"Timeout 60 seconds for {cpg_file}")
            continue

        graphs = prepare.json_process(PATHS.cpg, json_file, create_config.language)
        if graphs is None:
            print(f"Dataset chunk {s} not processed.")
            continue
        # dataset = data.create_with_index(graphs, ["Index", "cpg"])
        # dataset = data.inner_join_by_index(slice, dataset)
        print(f"Writing cpg dataset chunk {s}.")
        # data.write(dataset, PATHS.cpg, f"{s}_{FILES.cpg}.pkl")

        # del dataset
        os.remove(cpg_file_path)
        # os.remove(json_file_path)
        gc.collect()

def create_task():
    create_config = configs.CreateConfig()
    json_file = (
        "dataset.json" if create_config.language == "csharp" else "dataset.c.json"
    )
    raw = data.read(PATHS.raw, json_file)
    filter_func = None if create_config.language == "csharp" else None
    # c_project_filter_func
    filtered = data.apply_filter(raw, filter_func)
    filtered = data.clean(filtered)
    data.drop(filtered, ["commit_id"])
    slices = data.slice_frame(filtered, create_config.slice_size)
    slices = [(s, slice.apply(lambda x: x)) for s, slice in slices]

    cpg_files: list[str] = []
    log_file_path = os.path.join(PATHS.cpg, "joern_parse.log")

    # Delete log file if it exists
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print(f"Deleted old log file: {log_file_path}")

    # Create CPG binary files
    for s, slice in slices:
        data.to_files(slice, PATHS.joern, create_config.language)

        cpg_file = prepare.joern_parse(
            create_config, PATHS.joern, PATHS.cpg, f"{s}_{FILES.cpg}.bin"
        )
        print(f"Dataset {s} to cpg.")
        shutil.rmtree(PATHS.joern)

        # joern create
        joern_repl_binary = os.path.join(
            os.getcwd(),
            create_config.joern_cli_dir,
            "joern",
        )

        # TODO: fix "cpg_file.split('.')[0]" to be more robust
        json_file = f"{cpg_file.split('.')[0]}.json"
        cpg_file_path = os.path.join(os.getcwd(), PATHS.cpg, cpg_file)

        if not os.path.exists(cpg_file_path):
            continue

        cpg_file_path = f"{os.path.abspath(PATHS.cpg)}/{cpg_file}"
        json_file_path = f"{os.path.abspath(PATHS.cpg)}/{json_file}"
        script_path = f"{os.path.dirname(os.path.abspath(create_config.joern_cli_dir))}/graph-for-funcs.sc"

        cmd = " ".join(
            [
                joern_repl_binary,
                "-J-Xmx25G",
                f"--script {script_path}",
                f"--param cpgFile={cpg_file_path}",
                f"--param outFile={json_file_path}",
            ]
        )

        try:
            subprocess.run(
                cmd,
                text=True,
                check=True,
                shell=True,
                cwd=os.getcwd(),
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            print(f"Timeout 60 seconds for {cpg_file}")
            continue

        graphs = prepare.json_process(PATHS.cpg, json_file, create_config.language)
        if graphs is None:
            print(f"Dataset chunk {s} not processed.")
            continue
        dataset = data.create_with_index(graphs, ["Index", "cpg"])
        dataset = data.inner_join_by_index(slice, dataset)
        print(f"Writing cpg dataset chunk {s}.")
        data.write(dataset, PATHS.cpg, f"{s}_{FILES.cpg}.pkl")

        del dataset
        os.remove(cpg_file_path)
        os.remove(json_file_path)
        gc.collect()

def embed_task():
    embed_config = configs.EmbedConfig()
    # Tokenize source code into tokens
    dataset_files = data.get_directory_files(PATHS.cpg)
    w2vmodel = Word2Vec(**embed_config.w2v_args)
    w2v_init = True
    for pkl_file in dataset_files:
        file_name = pkl_file.split(".")[0]
        cpg_dataset = data.load(PATHS.cpg, pkl_file)
        tokens_dataset = data.tokenize(cpg_dataset)
        data.write(tokens_dataset, PATHS.tokens, f"{file_name}_{FILES.tokens}")
        # word2vec used to learn the initial embedding of each token
        w2vmodel.build_vocab(corpus_iterable=tokens_dataset.tokens, update=not w2v_init)
        w2vmodel.train(
            corpus_iterable=tokens_dataset.tokens,
            total_examples=w2vmodel.corpus_count,
            epochs=1,
        )
        if w2v_init:
            w2v_init = False
        # Embed cpg to node representation and pass to graph data structure
        cpg_dataset["nodes"] = cpg_dataset.apply(
            lambda row: cpg.parse_to_nodes(row.cpg, embed_config.nodes_dim), axis=1
        )
        # remove rows with no nodes
        cpg_dataset = cpg_dataset.loc[cpg_dataset.nodes.map(len) > 0]
        cpg_dataset["input"] = cpg_dataset.apply(
            lambda row: prepare.nodes_to_input(
                row.nodes,
                row.target,
                embed_config.nodes_dim,
                w2vmodel.wv,
                embed_config.edge_type,
            ),
            axis=1,
        )
        data.drop(cpg_dataset, ["nodes"])
        print(f"Saving input dataset {file_name} with size {len(cpg_dataset)}.")
        data.write(
            cpg_dataset[["input", "target"]], PATHS.input, f"{file_name}_{FILES.input}"
        )
        del cpg_dataset
        gc.collect()
    print("Saving w2vmodel.")
    w2vmodel.save(f"{PATHS.w2v}/{FILES.w2v}")


def process_task(stopping):
    process_config = configs.ProcessConfig()
    devign_config = configs.DevignConfig()
    model_path = PATHS.model + FILES.model
    os.makedirs(PATHS.model, exist_ok=True)

    model = process.Devign(
        path=model_path,
        device=DEVICE.type,
        model=devign_config.model,
        learning_rate=devign_config.learning_rate,
        weight_decay=devign_config.weight_decay,
        loss_lambda=devign_config.loss_lambda,
    )
    train = process.Train(model, process_config.epochs)
    input_dataset = data.loads(PATHS.input)
    # split the dataset and pass to DataLoader with batch size
    train_loader, val_loader, test_loader = list(
        map(
            lambda x: x.get_loader(
                process_config.batch_size, shuffle=process_config.shuffle
            ),
            data.train_val_test_split(input_dataset, shuffle=process_config.shuffle),
        )
    )
    train_loader_step = process.LoaderStep("Train", train_loader, DEVICE)
    val_loader_step = process.LoaderStep("Validation", val_loader, DEVICE)
    test_loader_step = process.LoaderStep("Test", test_loader, DEVICE)

    print(f"Start training")
    if stopping:
        early_stopping = process.EarlyStopping(model, patience=process_config.patience)
        train(train_loader_step, val_loader_step, early_stopping)
        model.load()
    else:
        train(train_loader_step, val_loader_step)
        model.save()

    process.predict(model, test_loader_step)


def main():
    """
    main function that executes tasks based on command-line options
    """
    parser: ArgumentParser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--prepare', help='Prepare task', required=False)
    parser.add_argument("-c", "--create", action="store_true")
    parser.add_argument("-e", "--embed", action="store_true")
    parser.add_argument("-p", "--process", action="store_true")
    parser.add_argument("-pS", "--process_stopping", action="store_true")

    args = parser.parse_args()

    if args.create:
        create_task()
        create_cpg_json()
    if args.embed:
        embed_task()
    if args.process:
        process_task(False)
    if args.process_stopping:
        process_task(True)


if __name__ == "__main__":
    main()
