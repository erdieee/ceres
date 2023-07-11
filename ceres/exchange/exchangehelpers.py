import asyncio
import logging


logger = logging.getLogger(__name__)


def retrier(f):
    async def wrapper(*args, **kwargs):
        count = kwargs.pop("count", 4)
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            msg = f'{f.__name__}() returned exception: "{e}". '
            if count > 0:
                msg += f"Retrying still for {count} times."
                count -= 1
                kwargs["count"] = count
                backoff_delay = (4 - (count + 1)) ** 2 + 1
                logger.info(f"Applying DDosProtection backoff delay: {backoff_delay}")
                await asyncio.sleep(backoff_delay)
                if msg:
                    logger.warning(msg)
                return await wrapper(*args, **kwargs)
            else:
                logger.warning(msg + "Giving up.")
                raise e

    return wrapper
