from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import openreview
from openreview import Note


@dataclass(frozen=True)
class Paper:
    id: str
    title: str
    authors: list[str]
    author_ids: list[str]
    keywords: list[str]
    tldr: str | None
    abstract: str
    primary_area: str | None
    venue: str
    venue_id: str
    pdf_url: str
    bibtex: str
    paperhash: str
    year: int

    def to_serializable(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "author_ids": self.author_ids,
            "keywords": self.keywords,
            "tldr": self.tldr,
            "abstract": self.abstract,
            "primary_area": self.primary_area,
            "venue": self.venue,
            "venue_id": self.venue_id,
            "pdf_url": self.pdf_url,
            "bibtex": self.bibtex,
            "paperhash": self.paperhash,
            "year": self.year,
        }

    @classmethod
    def from_note(cls, note: Note, year: int, use_v1: bool) -> "Paper":
        content = note.content
        return cls(
            id=content["paperhash"] if use_v1 else content["paperhash"]["value"],
            title=content["title"] if use_v1 else content["title"]["value"],
            authors=content["authors"] if use_v1 else content["authors"]["value"],
            author_ids=content["authorids"]
            if use_v1
            else content["authorids"]["value"],
            keywords=content["keywords"] if use_v1 else content["keywords"]["value"],
            tldr=content.get("one-sentence_summary", None)
            if use_v1
            else content.get("TLDR", {}).get("value", None),
            abstract=content["abstract"] if use_v1 else content["abstract"]["value"],
            primary_area=None if use_v1 else content["primary_area"]["value"],
            venue=content["venue"] if use_v1 else content["venue"]["value"],
            venue_id=content["venueid"] if use_v1 else content["venueid"]["value"],
            pdf_url=urljoin("https://openreview.net/", content["pdf"])
            if use_v1
            else urljoin("https://openreview.net/", content["pdf"]["value"]),
            bibtex=content["_bibtex"] if use_v1 else content["_bibtex"]["value"],
            paperhash=content["paperhash"] if use_v1 else content["paperhash"]["value"],
            year=year,
        )


def get_client(username: str, password: str, use_v1: bool) -> openreview.Client:
    if use_v1:
        return openreview.Client(
            baseurl="https://api.openreview.net", username=username, password=password
        )
    else:
        return openreview.api.OpenReviewClient(
            baseurl="https://api2.openreview.net", username=username, password=password
        )


def check_is_v1(year: int, venue: str, username: str, password: str) -> bool:
    client = get_client(username, password, use_v1=False)
    group = client.get_group(f"ICLR.cc/{year}/{venue}")
    domain = group.domain
    return not domain


def get_proceeding(year: int, venue: str, username: str, password: str) -> list[Paper]:
    use_v1 = check_is_v1(year, venue, username, password)

    client = get_client(username, password, use_v1)

    if use_v1:
        # Double-blind venues

        submissions = client.get_all_notes(
            invitation=f"ICLR.cc/{year}/{venue}/-/Blind_Submission", details="all"
        )
        blind_notes = {note.id: note for note in submissions}
        all_decision_notes = []
        for _, submission in blind_notes.items():
            all_decision_notes = all_decision_notes + [
                reply
                for reply in submission.details["directReplies"]
                if reply["invitation"].endswith("Decision")
            ]

        notes = []

        for decision_note in all_decision_notes:
            if "Accept" in decision_note["content"]["decision"]:
                notes.append(blind_notes[decision_note["forum"]])
    else:
        notes = client.get_all_notes(content={"venueid": f"ICLR.cc/{year}/{venue}"})

    papers = [Paper.from_note(note, year, use_v1) for note in notes]

    return papers
