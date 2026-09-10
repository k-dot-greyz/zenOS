"""ConversationProcessor reuses compiled regexes instead of compiling per call."""

from __future__ import annotations

import re

from zen.pkm.processor import ConversationProcessor


def test_word_pattern_is_precompiled():
    pattern = ConversationProcessor._WORD_PATTERN
    assert isinstance(pattern, re.Pattern)
    assert pattern.findall("hello, world!") == ["hello", "world"]
    assert pattern.findall("hello, world!") == re.findall(r"\b\w+\b", "hello, world!")


def test_code_block_pattern_is_precompiled():
    text = "before\n```python\nprint(1)\n```\nafter"
    pattern = ConversationProcessor._CODE_BLOCK_PATTERN
    assert isinstance(pattern, re.Pattern)
    assert pattern.findall(text) == ["```python\nprint(1)\n```"]
    assert pattern.findall(text) == re.findall(r"```[\s\S]*?```", text)


def test_list_pattern_is_precompiled_and_multiline():
    numbered = "intro\n1. first\n2. second"
    bullets = "- item\n* other"
    prose = "no list here 1. not at start"
    pattern = ConversationProcessor._LIST_PATTERN
    assert isinstance(pattern, re.Pattern)
    assert pattern.flags & re.MULTILINE
    assert pattern.search(numbered)
    assert pattern.search(bullets)
    assert pattern.search(prose) is None
    assert bool(pattern.search(numbered)) == bool(
        re.search(r"^\d+\.|^[-*]", numbered, re.MULTILINE)
    )
