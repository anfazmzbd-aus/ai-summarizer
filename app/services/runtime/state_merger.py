def merge_state(
    base,
    updates
):

    merged = (
        base.copy()
    )

    for key, value in updates.items():

        if key == "artifacts":

            merged.setdefault(
                "artifacts",
                {}
            )

            merged[
                "artifacts"
            ].update(
                value
            )

        else:

            merged[
                key
            ] = value

    return merged