#!/usr/bin/env python3
"""
Simple statistics script for BeaverDB conversation data.

Reports:
- Total messages and breakdown by role (user/assistant)
- Number of unique users who interacted
- Count of positive/negative feedback
"""

import os
import sys
from beaver import BeaverDB


BEAVER_DB_PATH = os.getenv("BEAVER_DB_PATH", "beaver.db")


def open_db(path: str) -> BeaverDB:
    if not os.path.exists(path):
        print(f"Database not found at {path}")
        sys.exit(1)
    return BeaverDB(path)


def main():
    db = open_db(BEAVER_DB_PATH)
    try:
        messages = db.list("global_messages")
        feedback = db.dict("global_feedback")

        total_messages = len(messages)
        user_messages = 0
        assistant_messages = 0
        unique_users = set()

        for msg in messages:
            role = msg.get("role")
            if role == "user":
                user_messages += 1
            elif role == "assistant":
                assistant_messages += 1

            uid = msg.get("user_id")
            if uid is not None:
                unique_users.add(uid)

        positive = sum(1 for v in feedback.values() if v.get("feedback") == "up")
        negative = sum(1 for v in feedback.values() if v.get("feedback") == "down")

        print("=== Conversation Stats ===")
        print(f"DB path:            {BEAVER_DB_PATH}")
        print(f"Total messages:     {total_messages}")
        print(f"- user messages:    {user_messages}")
        print(f"- assistant msgs:   {assistant_messages}")
        print(f"Unique users:       {len(unique_users)}")
        print(f"Feedback (positive): {positive}")
        print(f"Feedback (negative): {negative}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
