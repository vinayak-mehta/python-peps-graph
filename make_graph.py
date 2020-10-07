import sys

sys.path.insert(0, "peps")

from pep0.pep import PEP, PEPError

import os
import glob
import json


NON_EXISTENT_PEPS = ["0", "17", "30", "822", "9999", "9876"]

peps = {}
graph = {"nodes": [], "links": []}

for file_path in glob.glob("peps/*"):
    base_name = os.path.basename(file_path)

    if base_name.startswith("pep-0000."):
        continue

    if not os.path.isfile(file_path):
        continue

    if base_name.startswith("pep-") and file_path.endswith((".txt", "rst")):
        with open(file_path, "r", encoding="UTF-8") as pep_file:
            try:
                pep = PEP(pep_file)

                if pep.number != int(base_name[4:-4]):
                    raise PEPError(
                        "PEP number does not match file name", file_path, pep.number
                    )

                peps[pep.number] = []

                with open(file_path, "r", encoding="UTF-8") as pep0_file:
                    for line in pep0_file.readlines():
                        if "PEP" in line:
                            tokens = line.split(" ")
                            occurs = [i for i, t in enumerate(tokens) if "PEP" in t]
                            if len(occurs):
                                for occur in occurs:
                                    # "PEP8"
                                    found = "".join(filter(str.isdigit, tokens[occur]))
                                    if (
                                        found
                                        and len(found) <= 4
                                        and found not in NON_EXISTENT_PEPS
                                        and found not in peps[pep.number]
                                    ):
                                        peps[pep.number].append(str(int(found)))  # "0001"
                                    try:
                                        # "PEP" "8"
                                        found = "".join(
                                            filter(str.isdigit, tokens[occur + 1])
                                        )
                                        if (
                                            found
                                            and len(found) <= 4
                                            and found not in NON_EXISTENT_PEPS
                                            and found not in peps[pep.number]
                                        ):
                                            peps[pep.number].append(str(int(found)))  # "0001"
                                    except IndexError:
                                        pass
                                    if pep.number == 8:
                                        print(found)
            except PEPError as e:
                errmsg = "Error processing PEP %s (%s), excluding:" % (
                    e.number,
                    e.filename,
                )
                print(errmsg)

for pep, refs in peps.items():
    graph["nodes"].append({"id": str(pep), "group": 1, "label": f"P{pep}"})
    for ref in refs:
        graph["links"].append({"source": str(pep), "target": ref})

with open("data.json", "w") as f:
    json.dump(graph, f, indent=4, sort_keys=True)
