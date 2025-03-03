import json
import os
import re
import subprocess
from typing import Any

from configs import CreateConfig
from src.prepare.cpg_client_wrapper import CPGClientWrapper
import logging
from datetime import datetime

# from ..data import datamanager as data


def funcs_to_graphs(funcs_path):
    client = CPGClientWrapper()
    # query the cpg for the dataset
    print(f"Creating CPG.")
    graphs_string = client(funcs_path)
    # removes unnecessary namespace for object references
    graphs_string = re.sub(
        r"io\.shiftleft\.codepropertygraph\.generated\.", "", graphs_string
    )
    graphs_json = json.loads(graphs_string)

    return graphs_json["functions"]


def joern_parse(
    create_config: CreateConfig,
    input_path: str,
    output_path: str,
    out_file: str,
) -> str:
    binary_file = os.path.join(
        os.getcwd(),
        create_config.joern_cli_dir,
        "joern-parse",
    )

    rust_specific_config = [
        "--language RUSTLANG",
        "--frontend-args",
        f"--rust-parser-path {create_config.rust_parser_path}",
    ]

    cmd = " ".join(
        [
            binary_file,
            "-J-Xmx25G",
            input_path,
            "--output",
            os.path.join(output_path, out_file),
            *(rust_specific_config if create_config.language == "rust" else []),
        ]
    )

    # Define log file
    log_file_path = os.path.join(output_path, "joern_parse.log")

    with open(log_file_path, "a") as log_file:  # "a" mode appends to the file
        process = subprocess.Popen(
            cmd,
            text=True,
            shell=True,
            cwd=os.getcwd(),
            stdout=log_file,  # Redirect standard output to log file
            stderr=log_file,  # Redirect errors to the same log file
        )
        process.communicate()  # Wait for the process to finish

        if process.returncode != 0:
            print(f"Error: Joern parse process failed. Check the log at {log_file_path}")

    return out_file

# def joern_parse(
#     create_config: CreateConfig,
#     input_path: str,
#     output_path: str,
#     out_file: str,
# ) -> str:
#     binary_file = os.path.join(
#         os.getcwd(),
#         create_config.joern_cli_dir,
#         "joern-parse",
#     )

#     rust_specific_config = [
#         "--language RUSTLANG",
#         "--frontend-args",
#         f"--rust-parser-path {create_config.rust_parser_path}",
#     ]

#     cmd = " ".join(
#         [
#             binary_file,
#             "-J-Xmx25G",
#             input_path,
#             "--output",
#             os.path.join(output_path, out_file),
#             *(rust_specific_config if create_config.language == "rust" else []),
#         ]
#     )

#     # Define log file
#     log_file_path = os.path.join(output_path, "joern_parse.log")

#     with open(log_file_path, "a") as log_file:  # "a" mode appends to the file
#         process = subprocess.Popen(
#             cmd,
#             text=True,
#             shell=True,
#             cwd=os.getcwd(),
#             stdout=log_file,  # Redirect standard output to log file
#             stderr=log_file,  # Redirect errors to the same log file
#         )
#         process.communicate()  # Wait for the process to finish

#         if process.returncode != 0:
#             print(f"Error: Joern parse process failed. Check the log at {log_file_path}")

#     return out_file


def joern_create(
    create_config: CreateConfig, in_path: str, out_path: str, cpg_files: list[str]
) -> list[str]:
    joern_repl_binary = os.path.join(
        os.getcwd(),
        create_config.joern_cli_dir,
        "joern",
    )
    json_files: list[str] = []

    for cpg_file in cpg_files:
        # TODO: fix "cpg_file.split('.')[0]" to be more robust
        json_file_name = f"{cpg_file.split('.')[0]}.json"
        json_files.append(json_file_name)
        cpg_file_path = os.path.join(os.getcwd(), in_path, cpg_file)

        print(cpg_file_path)

        if not os.path.exists(cpg_file_path):
            continue

        cpg_file_path = f"{os.path.abspath(in_path)}/{cpg_file}"
        json_out = f"{os.path.abspath(out_path)}/{json_file_name}"
        script_path = f"{os.path.dirname(os.path.abspath(create_config.joern_cli_dir))}/graph-for-funcs.sc"

        cmd = " ".join(
            [
                joern_repl_binary,
                "-J-Xmx25G",
                f"--script {script_path}",
                f"--param cpgFile={cpg_file_path}",
                f"--param outFile={json_out}",
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

    return json_files


def graph_indexing(
    graph,
    language: str = "c",
) -> tuple[int, dict[str, list[Any]]]:
    match language:
        case "rust":
            file_ext = ".rs"
        case "csharp":
            file_ext = ".cs"
        case "c":
            file_ext = ".c"
        case _:
            file_ext = ".c"

    idx = int(graph["file"].split(file_ext)[0].split("/")[-1])
    del graph["file"]
    return (idx, {"functions": [graph]})


def json_process(
    in_path: str,
    json_file: str,
    language: str = "c",
):
    json_file_path = os.path.join(os.getcwd(), in_path, json_file)

    if not os.path.exists(json_file_path):
        return None

    with open(json_file_path) as f:
        cpg_string = f.read()
        cpg_string = re.sub(
            r"io\.shiftleft\.codepropertygraph\.generated\.", "", cpg_string
        )

        cpg_json = json.loads(cpg_string)
        container = [
            graph_indexing(graph, language)
            for graph in cpg_json["functions"]
            if graph["file"] not in ["<includes>", "<empty>", "N/A"]
        ]
        return container


"""
def generate(dataset, funcs_path):
    dataset_size = len(dataset)
    print("Size: ", dataset_size)
    graphs = funcs_to_graphs(funcs_path[2:])
    print(f"Processing CPG.")
    container = [graph_indexing(graph) for graph in graphs["functions"] if graph["file"] != "N/A"]
    graph_dataset = data.create_with_index(container, ["Index", "cpg"])
    print(f"Dataset processed.")

    return data.inner_join_by_index(dataset, graph_dataset)
"""

# client = CPGClientWrapper()
# client.create_cpg("../../data/joern/")
# joern_parse("../../joern/joern-cli/", "../../data/joern/", "../../joern/joern-cli/", "gen_test")
# print(funcs_to_graphs("/data/joern/"))
"""
while True:
    raw = input("query: ")
    response = client.query(raw)
    print(response)
"""
