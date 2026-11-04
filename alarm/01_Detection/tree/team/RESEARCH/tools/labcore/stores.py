"""labcore.stores (BUILD2, 23 Oct 2026): RE-EXPORTS of the stored-table readers (spec LEAD/LABCORE_STEP2_SPEC_V1.md b75998c5 sec 5). No code
of its own: profile_read, context_read, stamp_read ARE alarm_profile.read, alarm_context.read, alarm_stamp.read (the tools stay the owners)."""
import importlib.util, os

TOOLS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))


def _load(name):
    p = os.path.join(TOOLS, name, name + '.py')
    sp = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


alarm_profile = _load('alarm_profile'); alarm_context = _load('alarm_context'); alarm_stamp = _load('alarm_stamp')
profile_read = alarm_profile.read
context_read = alarm_context.read
stamp_read = alarm_stamp.read
