# powermon/protocols/parsers.py

from powermon.protocols.model import ParsedResponse

def parse_pi30_ascii(data: bytes) -> ParsedResponse:
    text = data.decode("ascii").strip()
    return ParsedResponse(fields=text.split(), raw=data)


def parse_pi30_flags(data: bytes) -> ParsedResponse:
    text = data.decode("ascii").strip()
    return ParsedResponse(fields=list(text), raw=data)