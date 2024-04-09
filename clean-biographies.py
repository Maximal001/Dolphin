import os


def clean():
    """
    Cleans all biographies (removes whitespaces, duplicate lines and double spaces). Then, saves inside 'biographies.txt'.
    """

    # Load Raw Biographies
    with open("./biographies-raw.txt", "r", encoding="utf-8") as file: raws: list[str] = list(set(file.read().strip().split("\n")))

    # Remove Empty Biographies
    raws.remove("")

    # Cleaned Biographies (List)
    array: list[str] = [each.strip().replace("  ", "") for each in raws]

    # Cleaned Biographies (Text)
    content: str = str().join([f"{each}\n" for each in array]).strip()

    # Save To File (Text)
    with open("./data/biographies.txt", "w", encoding="utf-8") as file: file.write(content)

    # Logging
    print(f"Parsed {len(array)} Biographies.")


if os.path.exists("./biographies-raw.txt") and os.path.isfile("./biographies-raw.txt"): clean()
else: print("Please put all biographies inside ./data/biographies-raw.txt file using new line as a separator.")
