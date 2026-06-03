from concurrent.futures import ThreadPoolExecutor


def execute_parallel(tasks):

    results = []

    with ThreadPoolExecutor() as executor:

        futures = [
            executor.submit(
                func,
                *args
            )
            for func, args in tasks
        ]

        for future in futures:
            results.append(
                future.result()
            )

    return results