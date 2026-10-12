"""The Codice Moderno: every invention in the codex, in folio order.

A folio's `draw` is None until its page has been drawn; the site lists it
as in preparation. `notes` translates every mirrored Italian line on the
page; build.py refuses to publish a page with an untranslated line.
"""

from __future__ import annotations

import importlib

from dataclasses import dataclass, field
from typing import Callable

from codex import Page
from folios import folio_airpods, folio_cybertruck
from pages.iphone import folio_iphone


@dataclass
class Folio:
    slug: str
    name: str
    year: int
    maker: str
    summary: str
    draw: Callable[[], Page] | None = None
    notes: dict[str, str] = field(default_factory=dict)


CATALOG: list[Folio] = [
    Folio("iphone", "iPhone", 2007, "Apple",
          "Announced in January 2007 as a phone, an iPod and an internet communicator in one device. "
          "Its multi-touch glass screen replaced the keyboard and set the shape of nearly every phone since.",
          draw=folio_iphone, notes={
              "Della tavoletta che parla": "Of the little tablet that speaks",
              "in questa tavoletta di vetro": "in this little tablet of glass",
              "sta il telefono e la musica": "are the telephone and the music",
              "e tutte le lettere del mondo": "and all the letters of the world",
              "si comanda col dito sanza tasti": "it is commanded with the finger, without keys",
              "a. il vetro che sente il tocco": "a. the glass that feels the touch",
              "b. la finestra della luce": "b. the window of light",
              "c. il cervello di rame": "c. the brain of copper",
              "d. il serbatoio della forza": "d. the reservoir of force",
              "e. la schiena di metallo": "e. the back of metal",
              "due dita che s'allargano": "two fingers spreading apart",
              "fanno la figura più grande": "make the picture larger",
              "g. il bottone che riporta a casa": "g. the button that brings you home",
          }),
    Folio("bionic-hand", "Bionic hand", 2007, "Touch Bionics",
          "The i-LIMB, released in Scotland in 2007, was the first commercially available prosthetic hand "
          "with individually powered fingers, driven by muscle signals read from the skin of the arm.",),
    Folio("atlas-detector", "ATLAS detector", 2008, "CERN",
          "One of the two general-purpose detectors on the Large Hadron Collider, which began operating in 2008. "
          "It is about 46 metres long and 25 metres high, and in 2012 it co-discovered the Higgs boson.",),
    Folio("sky-crane", "Mars sky crane", 2012, "NASA JPL",
          "To land the nearly one-tonne Curiosity rover on Mars in August 2012, NASA lowered it on cables from a "
          "hovering, rocket-powered crane, which then flew away and crashed at a safe distance."),
    Folio("humanoid-robot", "Humanoid robot", 2013, "Boston Dynamics",
          "Atlas was unveiled in 2013 for the DARPA Robotics Challenge and later learned to run, jump and backflip; "
          "an all-electric version followed in 2024. Leonardo sketched a mechanical knight around 1495."),
    Folio("airpods", "AirPods", 2016, "Apple",
          "Wireless earbuds released in December 2016. Each bud carries its own battery, chip and microphones "
          "in the stem, and the case recharges them, which made going without a cable feel ordinary.",
          draw=folio_airpods, notes={
              "Delli orecchini che cantano": "Of the little earrings that sing",
              "questo strumento si mette nell'orecchio": "this instrument is placed in the ear",
              "e porta la musica sanza alcuno filo": "and carries music without any wire",
              "per virtù d'una forza invisibile": "by virtue of an invisible force",
              "che passa per l'aria come la luce": "that passes through the air like light",
              "la sua virtù sta nel gambo": "its power lies in the stem",
              "dove si nasconde lo spirito suo": "where its spirit hides",
              "c. la membrana che trema e fa la voce": "c. the membrane that trembles and makes the voice",
              "d. il serbatoio della forza": "d. the reservoir of force",
              "le onde dell'aria si movono": "the waves of the air move",
              "come quelle dell'acqua quando": "like those of water when",
              "vi si getta una pietra": "a stone is thrown into it",
              "e. f. due fonti per due orecchie": "e. f. two sources for two ears",
              "la scatola bianca li nutrisce": "the white box nourishes them",
              "come la madre nutrisce li figlioli": "as a mother nourishes her children",
              "a. il perno ove si volge il coperchio": "a. the pin on which the lid turns",
              "b. il coperchio aperto": "b. the open lid",
          }),
    Folio("cybertruck", "Cybertruck", 2019, "Tesla",
          "Unveiled in November 2019 with a flat-panelled stainless steel body. At the launch, its 'armor glass' "
          "windows cracked when a metal ball was thrown at them. Deliveries began in 2023.",
          draw=folio_cybertruck, notes={
              "Del carro di ferro sanza cavalli": "Of the iron cart without horses",
              "questo carro si move per sé medesimo": "this cart moves by itself",
              "sanza cavalli e sanza vento": "without horses and without wind",
              "la forma sua è tutta di linee rette": "its form is all straight lines",
              "come uno triangolo posato in terra": "like a triangle laid on the ground",
              "a. b. c. il triangolo del corpo": "a. b. c. the triangle of the body",
              "il ferro non si piega": "the iron does not bend",
              "dinanzi. il lume è una sola linea": "from the front: the light is a single line",
              "le pietre non lo rompono  ma il vetro sì": "stones do not break it, but the glass, yes",
              "g. la forza chiusa in vasetti": "g. the force shut up in little jars",
              "h. il motore che gira per virtù di calamita": "h. the motor that turns by virtue of the magnet",
              "i. e la ruota seguita il motore": "i. and the wheel follows the motor",
          }),
    Folio("quantum-computer", "Quantum computer", 2019, "Google",
          "In 2019 Google's 53-qubit Sycamore chip, cooled to near absolute zero inside a gold 'chandelier' "
          "cryostat, ran a calculation Google estimated would take a supercomputer 10,000 years. IBM disputed the estimate."),
    Folio("euv-machine", "EUV chip machine", 2019, "ASML",
          "These machines hit droplets of molten tin with a laser about 50,000 times a second to make 13.5-nanometre "
          "light, then bounce it off ultra-smooth mirrors to print the finest features of modern chips."),
    Folio("ingenuity", "Ingenuity", 2021, "NASA JPL",
          "On 19 April 2021 this 1.8 kg helicopter made the first powered, controlled flight on another planet. "
          "Planned for five flights, it flew 72 before a damaged rotor ended its mission in January 2024."),
    Folio("james-webb", "James Webb Space Telescope", 2021, "NASA, ESA, CSA",
          "Launched on 25 December 2021. Its 6.5-metre mirror is made of 18 gold-coated hexagonal segments, "
          "shaded from the Sun by a five-layer shield the size of a tennis court."),
    Folio("neuralink", "Neuralink implant", 2024, "Neuralink",
          "In January 2024 a coin-sized implant with 64 threads thinner than a hair was placed in a human brain "
          "by a surgical robot, letting a paralysed man move a computer cursor by thought."),
    Folio("vision-pro", "Vision Pro", 2024, "Apple",
          "A headset released in February 2024 that puts 23 million pixels in front of the eyes and is "
          "controlled by where you look and small gestures of the hand."),
    Folio("starship-catch", "Starship tower catch", 2024, "SpaceX",
          "On 13 October 2024 the returning Super Heavy booster, about 70 metres tall, was caught in mid-air "
          "by two mechanical arms on its launch tower, nicknamed the chopsticks."),
]


# Folios drawn in their own module under pages/: each exports folio_<module>() and NOTES.
PAGE_MODULES = {
    "bionic-hand": "bionic_hand",
    "atlas-detector": "atlas",
    "sky-crane": "sky_crane",
    "humanoid-robot": "humanoid_robot",
    "quantum-computer": "quantum_computer",
    "euv-machine": "euv_machine",
    "ingenuity": "ingenuity",
    "james-webb": "james_webb",
    "neuralink": "neuralink",
    "vision-pro": "vision_pro",
    "starship-catch": "starship_catch",
}

for _f in CATALOG:
    if _f.slug in PAGE_MODULES:
        _name = PAGE_MODULES[_f.slug]
        _mod = importlib.import_module(f"pages.{_name}")
        _f.draw, _f.notes = getattr(_mod, f"folio_{_name}"), _mod.NOTES


def folio_label(i: int) -> str:
    return f"f. {i + 1}r"


def by_slug(slug: str) -> tuple[int, Folio]:
    for i, f in enumerate(CATALOG):
        if f.slug == slug:
            return i, f
    raise KeyError(slug)


def make_page(slug: str) -> Page:
    i, f = by_slug(slug)
    if f.draw is None:
        raise ValueError(f"{f.name} has not been drawn yet")
    page = f.draw()
    page.folio = folio_label(i)
    return page


def drawn() -> list[str]:
    return [f.slug for f in CATALOG if f.draw]
