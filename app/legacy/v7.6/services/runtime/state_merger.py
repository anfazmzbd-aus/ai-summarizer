from copy import deepcopy

def merge_state(
    base,
    updates,
    overwrite_agents=None
):

    overwrite_agents = (
        overwrite_agents
        or []
    )

    merged = deepcopy(
        base
    )

    merged.setdefault(
        "artifacts",
        {}
    )

    incoming = (
        updates.get(
            "artifacts",
            {}
        )
    )

    for key, value in incoming.items():

        if (
            key in merged["artifacts"]
            and key not in overwrite_agents
        ):

            continue

        merged[
            "artifacts"
        ][key] = deepcopy(
            value
        )

    return merged

def merge_retry_state(base, retry_results):

    merged = (
        deepcopy(
            base
        )
    )

    merged.setdefault("artifacts", {})

    for r in retry_results:

        artifacts = r.get("artifacts", {})

        for key, value in artifacts.items():

            if key not in merged["artifacts"]:
                merged["artifacts"][key] = deepcopy(value)
                continue

            # LIST MERGE (core fix)
            if isinstance(merged["artifacts"][key], list):
                merged["artifacts"][key].extend(deepcopy(value))
                continue

            # DICT MERGE (nested support)
            if isinstance(merged["artifacts"][key], dict):
                merged["artifacts"][key].update(deepcopy(value))
                continue

            # fallback overwrite
            merged["artifacts"][key] = deepcopy(value)

    return merged