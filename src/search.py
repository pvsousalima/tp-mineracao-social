from logging import getLogger
from typing import Iterator
from gogettr.utils import merge
from get import get_paginated

logger = getLogger(__name__)

MAX_POSTS_PER_REQUEST = 20
POSTS_PER_PAGE = 20

def pull(query: str, max_posts: int = None) -> Iterator[dict]:
    """
    Search for posts matching the given query on GETTR.

    :param query: The query to be passed to GETTR.
    :param max_posts: The maximum number of posts to retrieve.

    :return: An iterator yielding dictionaries representing posts.
    """
    url = "/u/posts/srch/phrase"
    posts_emitted = 0  # Number of posts emitted

    for data in get_paginated(
        url,
        params={
            "max": MAX_POSTS_PER_REQUEST,
            "q": query,
        },
        offset_step=POSTS_PER_PAGE,
    ):
        for event in data["data"]["list"]:
            post_id = event["activity"]["tgt_id"]
            user_id = event["activity"]["src_id"]

            if post_id not in data["aux"]["post"]:
                logger.warning("Unable to find post data for post %s", post_id)
                continue

            # Information about posts is spread across three objects, so we merge them together here.
            post = merge(
                event,
                data["aux"]["post"].get(post_id),
                data["aux"]["s_pst"].get(post_id),
                dict(uinf=data["aux"]["uinf"].get(user_id)),
            )

            # Verify that we haven't exceeded the maximum number of posts to retrieve
            if max_posts is not None and posts_emitted >= max_posts:
                return

            posts_emitted += 1
            yield post
