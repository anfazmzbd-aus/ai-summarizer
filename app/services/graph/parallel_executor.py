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