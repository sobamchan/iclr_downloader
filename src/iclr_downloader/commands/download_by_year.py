from argparse import ArgumentParser
import sienna
from pathlib import Path

from iclr_downloader.core import get_proceeding


def run():
    parser = ArgumentParser()
    parser.add_argument(
        "--year",
        "-y",
        type=int,
        required=True,
        help="Year to download the proceeding of.",
    )
    parser.add_argument(
        "--venue",
        "-v",
        type=str,
        required=True,
        help="Venue to download the proceeding of. E.g., `Conference`",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        required=True,
        help="Directory to save the results.",
    )
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    year: int = args.year
    venue: str = args.venue
    output_dir: Path = Path(args.output_dir)

    username: str = args.username
    password: str = args.password

    if not output_dir.exists():
        raise ValueError(f"{output_dir} does not exist):")

    papers = get_proceeding(year, venue, username, password)
    serialized_papers = [p.to_serializable() for p in papers]
    sienna.save(serialized_papers, output_dir / f"iclr.{year}.{venue}.jsonl")


if __name__ == "__main__":
    run()
