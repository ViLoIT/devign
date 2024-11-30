import json
import os
import re
import subprocess
import time
from typing import Any
from src.prepare.cpg_client_wrapper import CPGClientWrapper

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


def joern_parse(joern_path, input_path, output_path, file_name) -> str:
    out_file = file_name + ".bin"
    binary_file = os.path.join(
        os.getcwd(),
        "./" + joern_path + "joern-parse",
    )
    cmd = " ".join(
        [
            binary_file,
            input_path,
            "--output",
            output_path + out_file,
        ]
    )

    subprocess.run(
        cmd,
        text=True,
        check=True,
        shell=True,
        cwd=os.getcwd(),
    )
    return out_file


def joern_create(
    joern_path: str, in_path: str, out_path: str, cpg_files: list[str]
) -> list[str]:
    joern_repl_binary: str = "./" + joern_path + "joern"
    json_files: list[str] = []

    for cpg_file in cpg_files:
        json_file_name = f"{cpg_file.split('.')[0]}.json"
        json_files.append(json_file_name)

        print(in_path + cpg_file)

        if not os.path.exists(in_path + cpg_file):
            continue

        cpg_file_path = f"{os.path.abspath(in_path)}/{cpg_file}"
        json_out = f"{os.path.abspath(out_path)}/{json_file_name}"
        script_path = (
            f"{os.path.dirname(os.path.abspath(joern_path))}/graph-for-funcs.sc"
        )

        cmd = " ".join(
            [
                joern_repl_binary,
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
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            print(f"Timeout 60 seconds for {cpg_file}")

    return json_files


def graph_indexing(graph) -> tuple[int, dict[str, list[Any]]]:
    idx = int(graph["file"].split(".c")[0].split("/")[-1])
    del graph["file"]
    return (idx, {"functions": [graph]})


def json_process(in_path, json_file):
    if not os.path.exists(in_path + json_file):
        return None

    with open(in_path + json_file) as jf:
        cpg_string = jf.read()
        cpg_string = re.sub(
            r"io\.shiftleft\.codepropertygraph\.generated\.", "", cpg_string
        )

        cpg_json = json.loads(cpg_string)
        container = [
            graph_indexing(graph)
            for graph in cpg_json["functions"]
            if graph["file"] not in ["<includes>", "<empty>"]
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
