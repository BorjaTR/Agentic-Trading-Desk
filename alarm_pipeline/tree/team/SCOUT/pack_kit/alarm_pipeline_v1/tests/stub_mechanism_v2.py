#!/usr/bin/env python3
"""stub_mechanism_v2.py (SCO-A154): the red stub for test_mechanism_v2.py; writes nothing, refuses everything."""
import sys
def decide(shares, thr):
    return dict(mechanism='NONE')
def parse_map(text):
    return {}, None, []
if __name__ == '__main__':
    print('REFUSED STUB'); sys.exit(2)
