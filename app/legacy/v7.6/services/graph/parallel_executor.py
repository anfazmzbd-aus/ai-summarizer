from concurrent.futures import ThreadPoolExecutor
from app.services.logging.logger import logger

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

    logger.info(
        f"****PARALLEL EXECUTION:" 
        f"{results}"
    )
    return results

def reorder_results(results, execution_order):

    index_map = {
        name: i
        for i, name in enumerate(execution_order)
    }

    return sorted(
        results,
        key=lambda r: index_map.get(r["agent"], 999)
    )

def stabilize_parallel_order(results, group_order):

    index_map = {
        agent: i
        for i, agent in enumerate(group_order)
    }

    return sorted(
        results,
        key=lambda r: index_map.get(
            r["agent"],
            999
        )
    )