import asyncio
import json
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv


async def add_questions():
    env_path = Path(__file__).parent.parent / ".env"
    hangman_path = Path(__file__).parent / "hangman_words.json"
    quiz_path = Path(__file__).parent / "quiz_questions.json"

    load_dotenv(env_path)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@db:{DB_PORT}/{DB_NAME}"
    print(DB_URL)
    conn = await asyncpg.connect(DB_URL)
    with open(quiz_path, "r") as f:
        questions = json.load(f)["quiz_questions"]
        if await conn.fetch("SELECT 1 FROM quiz_questions LIMIT 1;"):
            print("Questions already exist in the database.")
            f.close()

        else:
            await conn.executemany(
                "INSERT INTO quiz_questions (word, definition) VALUES ($1, $2);",
                [(q["word"], q["definition"]) for q in questions],
            )

            print("Questions added successfully.")
    with open(hangman_path, "r") as f:
        questions = json.load(f)["hangman_words"]
        if await conn.fetch("SELECT 1 FROM hangman_words LIMIT 1;"):
            print("Questions already exist in the database.")
            f.close()
        else:
            await conn.executemany(
                "INSERT INTO hangman_words (word) VALUES ($1);",
                [(q["word"],) for q in questions],
            )

            print("Questions added successfully.")

    await conn.close()


def main():
    asyncio.run(add_questions())


if __name__ == "__main__":
    main()
