#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
"""
Breafs : 
Requirements : pip install tiktoken
References : 
"""

import tiktoken
from tiktoken.core import Encoding

def count(transcription):
    encoding: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(transcription)
    tokens_count = len(tokens)
    print(f"{tokens_count=}")
    return tokens_count


if __name__ == "__main":
    count("Hello world!!")


