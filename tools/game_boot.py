"""Diagnostic boot of the from-source build in the tools/game_trace.py WinUAE profile.

The built DuckTales replaces only the executable on a private, write-protected copy
of disk 1. Records whether the title screen and the VBlank server are reached, or
where it crashes (PC mapped through the link map). Diagnostic only: a build with
LINK_ONLY_STUBS is never behavior evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, struct, sys, time
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'docs' / 'toolchain.json').is_file())
# Set from the command line: the built game (tools/game_build.py output) and a
# fresh run directory under build/trace (the private trace staging root).
WORKER = ROOT / 'build'
RUN = ROOT / 'build' / 'trace' / 'boot'
GAME_DIR = ROOT / 'build' / 'game'
FRAMES = 1500
ORIGINAL = False
FLOPPY_SPEED = 100  # WinUAE floppy_speed: 100 = real drive timing, 0 = turbo
INPUT = None
INPUT_OFFSET = 0
DUMP_FROM = None
DUMP_EVERY = 0
SHOT_FROM = None  # optional dense screenshots: from this frame ...
SHOT_EVERY = 0    # ... every SHOT_EVERY frames
sys.path.insert(0, str(ROOT / 'tools'))
import game_trace as trace
import trace_harness as harness
from ofs import OFSDisk, words


def checksum_block(block):
    row = list(words(block))
    row[5] = 0
    row[5] = (-(sum(row) & 0xffffffff)) & 0xffffffff
    return struct.pack('>128I', *row)


def put_pointer_page(page, block_ids):
    row = list(words(page))
    count = len(block_ids)
    if count > 72:
        raise ValueError('OFS pointer page exceeds 72 pointers')
    row[2] = count
    row[6:78] = [0] * 72
    row[78-count:78] = list(reversed(block_ids))
    return checksum_block(struct.pack('>128I', *row))


def replace_ofs_file(image, filename, replacement):
    disk = OFSDisk(image)
    disk_report = disk.parse()
    entry = next(row for row in disk.entries if row['path'] == filename and row['kind'] == 'file')
    header = entry['header_block']
    old_data = [row['block'] for row in entry['data_blocks']]
    old_ext = list(entry['extension_blocks'])
    data_need = math.ceil(len(replacement) / 488)
    ext_need = math.ceil(max(0, data_need - 72) / 72)
    free = set(disk_report['bitmap']['free_blocks'])

    def take(existing, count):
        chosen = existing[:count]
        extra = count - len(chosen)
        if extra > 0:
            candidates = sorted(free.difference(chosen))
            if len(candidates) < extra:
                raise RuntimeError('private ADF has insufficient free blocks')
            chosen.extend(candidates[:extra])
        return chosen

    data_ids = take(old_data, data_need)
    ext_ids = take(old_ext, ext_need)
    used = set(data_ids) | set(ext_ids)
    free.update(set(old_data) - set(data_ids))
    free.update(set(old_ext) - set(ext_ids))
    free.difference_update(used)

    for index, block_id in enumerate(data_ids):
        payload = replacement[index * 488:(index + 1) * 488]
        row = [0] * 128
        row[0] = 8
        row[1] = header
        row[2] = index + 1
        row[3] = len(payload)
        row[4] = data_ids[index + 1] if index + 1 < len(data_ids) else 0
        raw = struct.pack('>128I', *row)
        block = raw[:24] + payload + bytes(488 - len(payload))
        image[block_id * 512:(block_id + 1) * 512] = checksum_block(block)

    header_page = image[header * 512:(header + 1) * 512]
    hrow = list(words(header_page))
    hrow[4] = data_ids[0] if data_ids else 0
    hrow[81] = len(replacement)
    hrow[126] = ext_ids[0] if ext_ids else 0
    image[header * 512:(header + 1) * 512] = put_pointer_page(struct.pack('>128I', *hrow), data_ids[:72])

    remaining = data_ids[72:]
    for index, block_id in enumerate(ext_ids):
        chunk, remaining = remaining[:72], remaining[72:]
        row = [0] * 128
        row[0] = 16
        row[1] = block_id
        row[125] = header
        row[126] = ext_ids[index + 1] if index + 1 < len(ext_ids) else 0
        row[127] = 0xfffffffd
        image[block_id * 512:(block_id + 1) * 512] = put_pointer_page(struct.pack('>128I', *row), chunk)
    if remaining:
        raise RuntimeError('OFS pointer extensions did not cover all data blocks')

    bitmap_id = disk_report['bitmap']['blocks'][0]
    bitmap = bytearray(image[bitmap_id * 512:(bitmap_id + 1) * 512])
    for block_id in range(2, 1760):
        bit_offset = 4 * (1 + (block_id - 2) // 32)
        value = struct.unpack_from('>I', bitmap, bit_offset)[0]
        mask = 1 << ((block_id - 2) % 32)
        value = (value | mask) if block_id in free else (value & ~mask)
        struct.pack_into('>I', bitmap, bit_offset, value)
    bitmap_words = list(words(bitmap))
    bitmap_words[0] = 0
    bitmap_words[0] = (-(sum(bitmap_words) & 0xffffffff)) & 0xffffffff
    image[bitmap_id * 512:(bitmap_id + 1) * 512] = struct.pack('>128I', *bitmap_words)

    verified = OFSDisk(bytes(image))
    verified_report = verified.parse()
    if verified.files.get(filename) != replacement:
        raise RuntimeError('OFS round trip did not preserve replacement bytes')
    return dict(path=filename, header_block=header, old_bytes=entry['size'], new_bytes=len(replacement),
                old_data_blocks=len(old_data), new_data_blocks=len(data_ids),
                old_extension_blocks=len(old_ext), new_extension_blocks=len(ext_ids),
                released_blocks=sorted((set(old_data) | set(old_ext)) - used),
                allocated_blocks=sorted(used - (set(old_data) | set(old_ext))),
                verified_sha256=hashlib.sha256(replacement).hexdigest(), free_blocks=len(verified_report['bitmap']['free_blocks'])), bytes(image)


def prepare():
    cfg = trace.runtime_config()
    if RUN.exists():
        pins = json.loads((RUN/'inputs.json').read_text(encoding='utf-8'))
        if pins['disks'][0]['sha256'] != cfg['disks'][0]['sha256'] or pins['disks'][1]['sha256'] != cfg['disks'][1]['sha256']:
            raise RuntimeError('existing diagnostic directory is not an untouched trace staging copy')
    else:
        trace.select_root(RUN)
        trace.stage_run(RUN, cfg, FLOPPY_SPEED)
    disk_path = RUN / 'disk1.adf'
    original_disk = disk_path.read_bytes()
    # --original boots the untouched original executable as a baseline.
    built = original_executable(original_disk) if ORIGINAL else (GAME_DIR / 'DuckTales').read_bytes()
    disk_path.chmod(0o644)
    report, updated = replace_ofs_file(bytearray(original_disk), 'DuckTales', built)
    disk_path.write_bytes(updated)
    disk_path.chmod(0o444)
    pins_path = RUN / 'inputs.json'
    pins = json.loads(pins_path.read_text(encoding='utf-8'))
    pins['disks'][0]['sha256'] = hashlib.sha256(updated).hexdigest()
    pins['disks'][0]['original_sha256'] = cfg['disks'][0]['sha256']
    pins['disks'][0]['replacement_sha256'] = report['verified_sha256']
    pins_path.write_text(json.dumps(pins, indent=2) + '\n', encoding='utf-8', newline='\n')
    # An input script recorded relative to the title screen can be shifted to
    # cold-boot frames with --input-offset.
    events = json.loads(Path(INPUT).read_text(encoding='utf-8')) if INPUT else trace.default_input()
    events = [dict(e, frame=e['frame'] + INPUT_OFFSET) for e in events if e['frame'] + INPUT_OFFSET < FRAMES]
    validated = trace.validate_input(events, FRAMES)
    (RUN / 'title-input.json').write_text(json.dumps(validated, indent=2) + '\n', encoding='utf-8', newline='\n')
    disk = OFSDisk(updated)
    disk_report = disk.parse()
    prepared = dict(run=str(RUN), profile='tools/game_trace.py private trace A500 PAL profile',
        volume=disk_report['volume'], startup_sequence=next((value.decode('latin-1') for name,value in disk.files.items() if name.lower() == 's/startup-sequence'), ''),
        disks=[dict(path=str(RUN/'disk1.adf'),sha256=pins['disks'][0]['sha256'],write_protected=True),
               dict(path=str(RUN/'disk2.adf'),sha256=pins['disks'][1]['sha256'],write_protected=True)],
        executable_sha256=report['verified_sha256'], replacement=report, frame_count=FRAMES,
        input_events=len(validated), screenshots_requested=[0,100,500,1000,FRAMES-1], diagnostic_only=True)
    (RUN / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(prepared, indent=2), flush=True)


# Kickstart 1.3 (the pinned ROM) exception entry points for bus error, address
# error and illegal instruction; read from the vector table of a booted image.
EXCEPTION_HANDLERS = {0xFC0818: 'bus error', 0xFC081A: 'address error', 0xFC081C: 'illegal instruction'}
CPU_EVENT = re.compile(r'(Illegal instruction: [0-9A-Fa-f]+ at [0-9A-Fa-f]+ -> [0-9A-Fa-f]+|Exception \d+[^\r\n]*|Address error[^\r\n]*|Bus error[^\r\n]*)')
ARM_EXCEPTIONS_AT = 760  # emulated frames: after Kickstart/DOS boot, before the game loads (~frame 800)
# Frame 0 of every run is the first frame that begins after START_CCK colour clocks from
# power-on (about 2.07 s, where the earlier wall-clock entry landed). Entering the debugger
# after a wall-clock pause stops anywhere within a few frames (measured 2026-10-18: one of
# three fresh sessions stopped 47,000 colour clocks earlier, and every later frame, input
# and RNG seed moved with it), so the run enters earlier and steps to this emulated point.
START_CCK = 7_330_000
CYCLE_UNIT = 512  # WinUAE's CYC counter: colour clocks x 512


def emulated_cck(emu):
    """Colour clocks since power-on (WinUAE's CIA view prints the cycle counter)."""
    found = re.search(r'CYC=([0-9A-Fa-f]+)', emu.cmd('c'))
    if not found:
        raise RuntimeError('no cycle counter in the CIA view')
    return int(found[1], 16) // CYCLE_UNIT


def step_to_start(emu):
    """Step whole frames until the first frame boundary at or after START_CCK."""
    entered = emulated_cck(emu)
    if entered >= START_CCK:
        raise RuntimeError('debugger entered after the start point (%d colour clocks)' % entered)
    while emulated_cck(emu) < START_CCK:
        boot_frame(emu)
    return entered


def exception_report(emu, state, model):
    """At an exception handler: the exception frame (SR, faulting PC) on the
    supervisor stack, registers and the user stack, symbolized where possible."""
    regs = emu.cmd('r')
    isp = re.search(r'ISP\s+([0-9A-Fa-f]{8})', regs)
    usp = re.search(r'USP\s+([0-9A-Fa-f]{8})', regs)
    report = dict(kind=EXCEPTION_HANDLERS[state['pc']], registers=regs[-1200:])
    words = []
    if isp:
        dump = emu.cmd('m %s 2' % isp.group(1))
        for line in dump.splitlines():
            m = re.match(r'([0-9A-Fa-f]{8})((?:\s+[0-9A-Fa-f]{4}){8})', line.strip())
            if m:
                words += m.group(2).split()
    if len(words) >= 3:
        # 68000 group 2 frame: SR, PC; bus/address errors push 4 more words first.
        start = 4 if report['kind'] != 'illegal instruction' else 0
        report['sr'] = words[start]
        report['pc'] = int(words[start+1] + words[start+2], 16)
        report['supervisor_words'] = words[:16]
        report['code_at_pc'] = emu.cmd('d %X 6' % max(0, report['pc'] - 8))[-900:]
    if usp:
        report['user_stack'] = emu.cmd('m %s 4' % usp.group(1))[-900:]
    return report


_DUMP = {}


def locate_program(emu, executable, model):
    """The program's DATA and CODE bases, found once in memory; False until loaded."""
    if not _DUMP.get('base'):
        # Retried until the program is loaded: before that no hunk is found, and while
        # it loads a DOS buffer can hold a second copy (ambiguous or partial match).
        try:
            mapping = harness.locate(emu.memory(), executable, model, harness.signatures(executable, model))
        except (AssertionError, ValueError, KeyError):
            return
        resident = mapping.get('resident') or {}
        _DUMP['base'] = resident.get(1, resident.get('1'))
        _DUMP['code'] = resident.get(0, resident.get('0'))
        _DUMP['size'] = model['hunks'][1]['allocated_size']
        (RUN / 'state-layout.json').write_text(json.dumps(dict(data_base=_DUMP['base'], data_size=_DUMP['size'],
            resident=resident), indent=2) + '\n', encoding='utf-8')
    return bool(_DUMP.get('base'))


def state_dump(emu, executable, model, frame_number, poll=None):
    """Append the program's DATA hunk (initialized data and its BSS tail) to
    state.bin and index it; the hunk base is located once in memory."""
    if not locate_program(emu, executable, model):
        return
    raw = emu.dump('state-frame.bin', _DUMP['base'], _DUMP['size'])
    with open(RUN / 'state.bin', 'ab') as out:
        offset = out.tell(); out.write(raw)
    with open(RUN / 'state-index.jsonl', 'a', encoding='utf-8') as index:
        row = dict(frame=frame_number, offset=offset, size=len(raw))
        if poll is not None:
            row['poll'] = poll
        index.write(json.dumps(row) + '\n')


RNG_STATE_OFFSET = 0x3AB8  # G_h01_3AB8: the game's 16-bit LFSR state (resident_F_463E)


def lfsr_step(x):
    """resident_F_463E: t = x + 0x9248; x = (t >> 3) ^ (t << 13), 16 bits."""
    t = (x + 0x9248) & 0xFFFF
    return ((t >> 3) ^ (t << 13)) & 0xFFFF


def is_reseed(previous, value, limit=256):
    """A change of the LFSR state that no run of LFSR steps explains is a reseed
    (resident_F_4676 stores VPOSR + tick: randomness drawn from beam timing)."""
    if previous is None or value == previous:
        return False
    x = previous
    for _ in range(limit):
        x = lfsr_step(x)
        if x == value:
            return False
    return True


class RngPin:
    """--rng-record logs every reseed of the game's RNG; --rng-pin RUN writes the
    k-th seed recorded in RUN at the k-th reseed. The original seeds from the
    video beam position, so a build that is not cycle-identical draws different
    random outcomes; pinning the seed separates that from logic differences."""

    def __init__(self, offset, pinned=None):
        self.offset, self.pinned, self.previous, self.events = offset, pinned, None, []
        self.first_observed = None

    def after_frame(self, emu, frame_number):
        base = _DUMP.get('base')
        if not base:
            return
        lines = [l for l in emu.cmd('m %X 1' % (base + self.offset)).splitlines()
                 if re.match(r'\s*[0-9A-Fa-f]{8} [0-9A-Fa-f]{4}', l)]
        if not lines:
            return
        value = int(lines[-1].split()[1], 16)
        if self.previous is None:
            self.first_observed = dict(frame=frame_number, value=value)
        if is_reseed(self.previous, value):
            event = dict(index=len(self.events), frame=frame_number, value=value, previous=self.previous)
            if self.pinned is not None and event['index'] < len(self.pinned):
                pinned = self.pinned[event['index']]['value']
                emu.cmd('W %X %02X %02X' % (base + self.offset, pinned >> 8, pinned & 0xFF))
                event['pinned'] = value = pinned
            self.events.append(event)
        if self.previous is None or is_reseed(self.previous, value):
            self.save()
        self.previous = value

    def seeded(self, emu, frame_number):
        """At seed_random's entry (poll-driven runs): run it to its rts and take the seed it
        stored - exact, where the per-frame check above infers reseeds from LFSR reachability."""
        emu.cmd('fi')                                        # seed_random calls nothing: its rts
        base = _DUMP['base']
        lines = [l for l in emu.cmd('m %X 1' % (base + self.offset)).splitlines()
                 if re.match(r'\s*[0-9A-Fa-f]{8} [0-9A-Fa-f]{4}', l)]
        value = int(lines[-1].split()[1], 16)
        event = dict(index=len(self.events), frame=frame_number, value=value, exact=True)
        if self.pinned is not None and event['index'] < len(self.pinned):
            pinned = self.pinned[event['index']]['value']
            emu.cmd('W %X %02X %02X' % (base + self.offset, pinned >> 8, pinned & 0xFF))
            event['pinned'] = pinned
        self.events.append(event)
        self.previous = event.get('pinned', value)
        self.save()

    def save(self):
        (RUN / 'rng-reseeds.json').write_text(json.dumps(dict(first_observed=self.first_observed, events=self.events),
                                                         indent=1) + '\n', encoding='utf-8')


RNG = None
POLLS = None
REPLAY = None   # --replay LOG: inputs at poll frames instead of the frame-stamped --input script

POLL_OFFSET = 0x4376  # poll_controller_and_keyboard_input, the game's one input read (root hunk)
SEED_OFFSET = 0x4676  # seed_random: the RNG state from VPOSR + game_frame_tick
VBLANK_OFFSET = 0x615E  # vblank_server: runs at the start of every frame
SOUND_OFFSET = 0x57D2   # play_sound: the game's sound commands (compared as events)
WAIT_OFFSETS = (0x86A8, 0x8C04)   # the Delay and WaitBOVP glue: the game waits for time
FRAME_CCK = 227 * 313  # colour clocks in a PAL frame
POLL_TIMEOUT = 120     # seconds of emulation without any input poll before the run counts as stuck
JOYSTICK_EVENTS = {'JOY2_RIGHT': 'right', 'JOY2_LEFT': 'left', 'JOY2_UP': 'up', 'JOY2_DOWN': 'down'}


def joy1dat(held):
    """JOY1DAT for the held directions: right bit 1, left bit 9, down bit 0 ^ bit 1,
    up bit 8 ^ bit 9 (as port/main.c builds it from keys)."""
    value = (2 if 'right' in held else 0) | (0x200 if 'left' in held else 0)
    value |= 1 if ('down' in held) != ('right' in held) else 0
    value |= 0x100 if ('up' in held) != ('left' in held) else 0
    return value


def replay_events(log):
    """A replay log (port/main.c format, poll frames) as WinUAE input events: (poll frame, events)
    with each JOY1DAT change split into direction presses and releases; and its seeds."""
    rows, seeds, held = [], [], set()
    directions = (('right', 0x2), ('left', 0x200))
    for line in Path(log).read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) != 3 or line.startswith('#'):
            continue
        at, kind, value = int(parts[0]), parts[1], int(parts[2], 16)
        if kind == 'seed':
            seeds.append(value)
        elif kind == 'fire':
            rows.append(dict(poll=at, event='JOY2_FIRE_BUTTON', value=value))
        elif kind == 'joy':
            now = {d for d, bit in directions if value & bit}
            if bool(value & 1) != ('right' in now):
                now.add('down')
            if bool(value & 0x100) != ('left' in now):
                now.add('up')
            for d in sorted(held - now):
                rows.append(dict(poll=at, event='JOY2_' + d.upper(), value=0))
            for d in sorted(now - held):
                rows.append(dict(poll=at, event='JOY2_' + d.upper(), value=1))
            held = now
    return rows, seeds


def port_replay_log(injected, seeds):
    """The run's inputs as a port replay log (port/main.c): each event at the poll frame that
    read it (`injected`: [(poll frame, WinUAE event)]); seeds are the recorded RNG reseeds."""
    lines, held = ['# from tools/game_boot.py: WinUAE inputs at the poll frame that read them'], set()
    for at, event in injected:
        if event['event'] == 'JOY2_FIRE_BUTTON':
            lines.append('%d fire %04x' % (at, 1 if event['value'] else 0))
        elif event['event'] in JOYSTICK_EVENTS:
            (held.add if event['value'] else held.discard)(JOYSTICK_EVENTS[event['event']])
            lines.append('%d joy %04x' % (at, joy1dat(held)))
        else:
            raise ValueError('no port input for WinUAE event ' + event['event'])
    lines += ['0 seed %04x' % value for value in seeds]
    return '\n'.join(lines) + '\n'


class PollFrames:
    """--poll-dumps: the run is driven by the game's input polls (poll_driven). A poll starts a
    new poll frame when the game has waited for time (Delay, WaitBOVP) since the current one
    began, or when it also polled in the frame just before (a loop polling every frame while a
    sound plays). Work that spans frames - drawing, decompressing, loading - does not, so the
    port, which spends no frames on it, counts the same steps (port/main.c platform_poll):
    inputs and checkpoints timed in poll frames mean the same game step on both machines."""

    def __init__(self, every):
        self.every, self.address, self.count, self.injected = every, None, 0, []
        self.seed = self.vblank = self.sound = None
        self.waits, self.waited, self.last_frame = (), False, None
        self.sounds = []                                   # (poll frame, sound command)


def run_to(emu, *addresses, timeout=POLL_TIMEOUT):
    """Run until the CPU enters one of `addresses`; the breakpoints are removed again."""
    for address in addresses:
        emu.cmd('f %X' % address)
    before = emu.snap(); emu.cmd('g', wait=False); emu.reconnect_console()
    text = emu.wait_prompt(before=before, timeout=timeout)
    emu.cmd('fd')
    return text


def poll_driven(emu, polls, start_cck, frames, pending, rng, dump, records):
    """The run from here on, stopping only at events: the game's input poll, seed_random and
    the start of a frame (its VBlank server). At the first poll of a frame: inject the
    script's events due by that frame (the poll reads them at once, as it would have read
    them at the frame's start - measured: fire injected at the entry is in the poll's
    result), count the poll frame, dump every N-th one; then wait for the next frame's
    VBlank before watching for polls again, so a busy loop's hundreds of polls per frame cost
    one stop. At seed_random: take the seed exactly (RngPin.seeded). Frames without a poll -
    loading, drawing - run at emulation speed. Frame steps are not used: with a breakpoint
    armed, WinUAE's frame steps run past their target line, and its memory watches do not
    fire during frame steps (measured 2026-10-18); debugger stops do not change the
    emulation (the same frames stepped two ways give identical memory)."""
    after_poll = False
    while True:
        watched = [polls.vblank if after_poll else polls.address] + ([polls.seed] if rng is not None else []) + \
            ([polls.sound] if polls.sound else []) + list(polls.waits)
        state = trace.cpu(run_to(emu, *watched))
        frame = (emulated_cck(emu) - start_cck) // FRAME_CCK
        if frame >= frames:
            return frame
        if rng is not None and state['pc'] == polls.seed:
            rng.seeded(emu, frame)
            continue
        if state['pc'] == polls.vblank:
            after_poll = False
            continue
        if state['pc'] in polls.waits:
            polls.waited = True
            continue
        if state['pc'] == polls.sound:                   # play_sound(n): n is the word above the return address
            line = [l for l in emu.cmd('m %X 1' % (state['regs']['A7'] + 4)).splitlines()
                    if re.match(r'\s*[0-9A-Fa-f]{8} [0-9A-Fa-f]{4}', l)][-1]
            polls.sounds.append((polls.count, int(line.split()[1], 16)))
            continue
        if state['pc'] != polls.address:
            raise RuntimeError('stopped outside the watched entries at %X' % state['pc'])
        fresh = polls.count == 0 or polls.waited or polls.last_frame == frame - 1
        polls.last_frame = frame
        after_poll = True
        if not fresh:
            continue                                     # the same poll frame continues
        polls.waited = False
        while pending and (pending[0]['poll'] <= polls.count + 1 if 'poll' in pending[0] else
                           pending[0]['frame'] <= frame):
            event = pending.pop(0)
            emu.cmd('I evt ' + event['event'] + ' ' + str(event['value']))
            polls.injected.append((polls.count + 1, event))
        polls.count += 1
        if polls.every and polls.count % polls.every == 0:
            dump(frame, polls.count)
        records.append(dict(frame=frame, poll=polls.count, pc=state['pc'], pc_hex=hex(state['pc']),
                            beam=[state['vpos'], state['hpos']]))


def symbol_offset(sym_path, hunk_number, name):
    current = None
    for line in sym_path.read_text(encoding='utf-8', errors='replace').splitlines():
        heading = re.match(r'Segment\s+\d+:\s+Hunk\s+(\d+)', line)
        if heading:
            current = int(heading.group(1)); continue
        match = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if current == hunk_number and match and match.group(2) == name:
            return int(match.group(1), 16)
    raise KeyError(name)


def write_port_replay(polls):
    """port-replay.log for a poll-driven run (docs/sdl3-port.md): its inputs at the poll
    frames that read them, and the seeds seed_random stored (taken exactly)."""
    if polls is None:
        return None
    record = json.loads((RUN / 'rng-reseeds.json').read_text()) if (RUN / 'rng-reseeds.json').exists() else {}
    seeds = [e.get('pinned', e['value']) for e in record.get('events', []) if e.get('exact')]
    text = port_replay_log(polls.injected, seeds) + ''.join('%d sound %04x\n' % s for s in polls.sounds) + \
        '%d end\n' % polls.count
    (RUN / 'port-replay.log').write_text(text, encoding='utf-8', newline='\n')
    return dict(path='port-replay.log', seeds=len(seeds), poll_frames=polls.count)


def boot_frame(emu):
    """Advance one emulated frame by raster (line 1, then line 0) and record
    where the CPU stopped. Unlike checkpoint traces, a cold boot has no game
    VBlank server to sync on, and interrupt work may delay the stop past line 0."""
    a = emu.cmd('fs 1'); b = emu.cmd('fs 0 0')
    state = trace.cpu(b)
    # WinUAE reports CPU faults in its console as they happen; keep those lines.
    # (Debugger breakpoints combined with frame stepping stall its console.)
    state['cpu_events'] = CPU_EVENT.findall(a + b)
    return state


def final_state(emu, model, root_base, words=32):
    """Registers, stack and symbolized return addresses at the end of a run."""
    regs = emu.cmd('r')
    sp = re.search(r'A7\s+([0-9A-Fa-f]{8})', regs)
    state = dict(registers=regs[-1200:], stack=[])
    if not sp:
        return state
    dump = emu.cmd('m %s %d' % (sp.group(1), (words * 4 + 15) // 16))
    values = []
    for line in dump.splitlines():
        m = re.match(r'([0-9A-Fa-f]{8})((?:\s+[0-9A-Fa-f]{4}){8})', line.strip())
        if m:
            halves = m.group(2).split()
            values += [int(halves[i] + halves[i+1], 16) for i in range(0, 8, 2)]
    root_size = model['hunks'][0]['allocated_size']
    for value in values[:words]:
        row = dict(value=hex(value))
        if root_base and root_base <= value < root_base + root_size:
            row['root_symbol'] = symbol_at(GAME_DIR/'DuckTales.sym', 0, value - root_base)
            text = emu.cmd('m %X 2' % value)
            chars = ''.join(re.findall(r'  (.{16})$', l)[0] if re.findall(r'  (.{16})$', l) else '' for l in text.splitlines())
            printable = re.match(r'[ -~]{6,}', chars)
            if printable:
                row['string'] = printable.group(0)
        state['stack'].append(row)
    return state


def original_executable(disk_bytes):
    disk = OFSDisk(bytes(disk_bytes)); disk.parse()
    return disk.files['DuckTales']


def symbol_at(sym_path, hunk_number, offset):
    if ORIGINAL:
        return None  # the baseline has no link map
    current = None
    found = []
    for line in sym_path.read_text(encoding='utf-8', errors='replace').splitlines():
        heading = re.match(r'Segment\s+\d+:\s+Hunk\s+(\d+)', line)
        if heading:
            current = int(heading.group(1))
            continue
        match = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if current == hunk_number and match:
            value = int(match.group(1), 16)
            if value <= offset:
                found.append((value, match.group(2)))
    if not found:
        return None
    value, name = max(found)
    return dict(symbol=name, hunk_offset=offset, symbol_offset=value, delta=offset-value)


def boot():
    import hunk
    trace.select_root(RUN)
    events = trace.validate_input(json.loads((RUN/'title-input.json').read_text(encoding='utf-8')), FRAMES)
    by_frame = {}
    for event in events:
        by_frame.setdefault(event['frame'], []).append(event)
    screenshots_dir = RUN / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_frames = set(range(0, FRAMES, 250)) | {FRAMES-1}
    if SHOT_EVERY and SHOT_FROM is not None:
        screenshot_frames |= set(range(SHOT_FROM, FRAMES, SHOT_EVERY))
    screenshot_paths = {}
    executable = original_executable((RUN/'disk1.adf').read_bytes()) if ORIGINAL else (GAME_DIR/'DuckTales').read_bytes()
    model = hunk.parse(executable)
    emu = harness.Emulator(RUN.name)
    outcome = dict(started_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   requested_frames=FRAMES, frames_completed=0, title_screen='NOT_YET_ASSESSED',
                   vblank_server_registered=None, crash=None, screenshots=screenshot_paths,
                   diagnostic_only=True, behavior_evidence=False)
    records = []
    try:
        # Deterministic: frame 0 is a fixed emulated point since power-on
        # (step_to_start), so runs (and the original vs a build) line up frame for frame.
        emu.start()
        time.sleep(1)
        initial = emu.enter()
        outcome['entered_at_cck'] = step_to_start(emu)
        outcome['start_cck'] = emulated_cck(emu)
        # Exception breakpoints are armed after Kickstart has booted (its CPU-type
        # probe executes an illegal MOVEC at reset), so the first hit is the program's.
        root_base = None  # nothing is loaded at power-on; mapped at the end
        outcome['initial_pc'] = trace.cpu(initial)['pc'] if re.search(r'VPOS:', initial) else None
        for frame_number in range(FRAMES):
            for event in by_frame.get(frame_number, []):
                emu.cmd('I evt ' + event['event'] + ' ' + str(event['value']))
                if POLLS is not None:
                    POLLS.injected.append((1, event))           # before the game's first poll
            before = {p for p in RUN.rglob('*.png')}
            if frame_number in screenshot_frames:
                emu.cmd('I evt SPC_SCREENSHOT 1')
                emu.cmd('I evt SPC_SCREENSHOT 0')
            try:
                if POLLS is not None and POLLS.address is None and DUMP_FROM is not None and \
                        frame_number >= DUMP_FROM and (frame_number - DUMP_FROM) % 25 == 0 and \
                        locate_program(emu, executable, model):
                    entry = lambda offset, name: _DUMP['code'] + (offset if ORIGINAL else
                                    symbol_offset(GAME_DIR / 'DuckTales.sym', 0, name))
                    POLLS.address = entry(POLL_OFFSET, '_F_h00_4376')
                    POLLS.seed = entry(SEED_OFFSET, '_F_h00_4676')
                    POLLS.vblank = entry(VBLANK_OFFSET, '_recon_h00_615E')
                    POLLS.sound = entry(SOUND_OFFSET, '_recon_h00_57D2')
                    POLLS.waits = (entry(WAIT_OFFSETS[0], '_Delay'), entry(WAIT_OFFSETS[1], '_WaitBOVP'))
                state = boot_frame(emu)
                if RNG is not None:
                    RNG.after_frame(emu, frame_number)
                if state.get('cpu_events') and frame_number >= ARM_EXCEPTIONS_AT:
                    outcome['exception'] = dict(frame=frame_number, events=state['cpu_events'],
                                                final=final_state(emu, model, None))
                    outcome['frames_completed'] = frame_number
                    break
            except Exception as exc:
                snapshot = emu.snap(2000)[1]
                pc = None
                try:
                    pc = trace.cpu(snapshot)['pc']
                except Exception:
                    pass
                root_size = model['hunks'][0]['allocated_size']
                sym = symbol_at(GAME_DIR/'DuckTales.sym', 0, pc-root_base) if pc is not None and root_base and root_base <= pc < root_base+root_size else None
                outcome['crash'] = dict(frame=frame_number, error=repr(exc), pc=pc, pc_hex=(hex(pc) if pc is not None else None),
                    map_symbol=sym, console_tail=snapshot[-5000:], guru_match=re.search(r'Guru[^\r\n]*',snapshot,re.I).group(0) if re.search(r'Guru[^\r\n]*',snapshot,re.I) else None)
                break
            record = dict(frame=frame_number, pc=state['pc'], pc_hex=hex(state['pc']), beam=[state['vpos'],state['hpos']])
            root_size = model['hunks'][0]['allocated_size']
            if root_base and root_base <= state['pc'] < root_base+root_size:
                record['pc_symbol'] = symbol_at(GAME_DIR/'DuckTales.sym', 0, state['pc']-root_base)
            records.append(record)
            if POLLS is None and DUMP_EVERY and DUMP_FROM is not None and frame_number >= DUMP_FROM and (frame_number - DUMP_FROM) % DUMP_EVERY == 0:
                state_dump(emu, executable, model, frame_number)
            outcome['frames_completed'] = frame_number+1
            if POLLS is not None and POLLS.address is not None:
                # The program is loaded: from here on the run is driven by the game's polls.
                pending = REPLAY or [event for f in sorted(by_frame) if f > frame_number for event in by_frame[f]]
                try:
                    poll_driven(emu, POLLS, outcome['start_cck'], FRAMES, pending, RNG if RNG else None,
                                lambda f, n: state_dump(emu, executable, model, f, poll=n), records)
                except Exception as exc:
                    snapshot = emu.snap(2000)[1]
                    outcome['crash'] = dict(poll_frame=POLLS.count, error=repr(exc), console_tail=snapshot[-5000:])
                    break
                outcome['frames_completed'] = FRAMES
                break
            after = sorted(set(RUN.rglob('*.png')) - before)
            if frame_number in screenshot_frames:
                if after:
                    source = after[-1]
                    target = screenshots_dir / ('frame_%04d' % frame_number + source.suffix.lower())
                    source.replace(target)
                    screenshot_paths[str(frame_number)] = str(target.relative_to(WORKER).as_posix())
                else:
                    screenshot_paths[str(frame_number)] = 'SCREENSHOT_EVENT_DID_NOT_CREATE_FILE'
            if frame_number % 100 == 0 or frame_number in screenshot_frames:
                print('FRAME', frame_number, 'PC', hex(state['pc']), 'screenshots', screenshot_paths.get(str(frame_number)), flush=True)
        # Same session, no relaunch: registers, the stack with root-code return
        # addresses symbolized through the link map, and any printable string a
        # stack word points at (e.g. a shutdown message argument).
        memory = emu.memory()
        mapping = harness.locate(memory, executable, model, harness.signatures(executable, model))
        (RUN/'mapping.json').write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')
        resident = mapping.get('resident') or {}
        root_base = resident.get(0, resident.get('0'))
        outcome['resident_bases'] = resident
        if not root_base:
            outcome['mapping_note'] = 'executable not found in memory at the end; no PC symbolization'
        outcome['final_state'] = final_state(emu, model, root_base)
        ti_end = emu.cmd('Ti')
        (RUN/'interrupt-servers-end.txt').write_text(ti_end, encoding='utf-8')
        outcome['vblank_server_registered_end'] = bool(re.search(r"\(C=([0-9a-fA-F]+) D=[0-9a-fA-F]+\) 'IT V Blank'", ti_end))
        outcome['elapsed_at_end'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    except Exception as exc:
        outcome['fatal_error'] = repr(exc)
        raise
    finally:
        emu.close()
        outcome['process_cleanup'] = json.loads((RUN/'cleanup.json').read_text(encoding='utf-8')) if (RUN/'cleanup.json').exists() else None
        (RUN/'frame-log.jsonl').write_text(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in records), encoding='utf-8', newline='\n')
        if POLLS is not None:
            outcome['poll_frames'] = dict(count=POLLS.count, address=POLLS.address)
        try:
            outcome['port_replay'] = write_port_replay(POLLS)
        except (OSError, KeyError, ValueError) as exc:
            outcome['port_replay'] = dict(error=repr(exc))
        (RUN/'boot-report.json').write_text(json.dumps(outcome, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(outcome, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diagnostic WinUAE boot of a from-source build (never behavior evidence).')
    parser.add_argument('action', choices=['prepare','boot','run'])
    parser.add_argument('--game-dir', type=Path, default=GAME_DIR)
    parser.add_argument('--run-name', default='boot')
    parser.add_argument('--frames', type=int, default=FRAMES)
    parser.add_argument('--original', action='store_true', help='boot the original executable (baseline)')
    parser.add_argument('--input', help='input event script (JSON); default: the title script')
    parser.add_argument('--input-offset', type=int, default=0, help='frames added to every input event')
    parser.add_argument('--dump-from', type=int, help='first frame of DATA+BSS state dumps (state.bin)')
    parser.add_argument('--dump-every', type=int, default=0, help='dump interval in frames (0: no dumps)')
    parser.add_argument('--turbo-floppy', action='store_true',
                        help='WinUAE turbo floppy: load times stop depending on where files sit on disk')
    parser.add_argument('--screenshot-from', type=int, help='dense screenshots from this frame (with --screenshot-every)')
    parser.add_argument('--screenshot-every', type=int, default=0, help='dense screenshot interval in frames')
    parser.add_argument('--poll-dumps', type=int, metavar='N',
                        help='count poll frames (frames in which the game reads its input) and dump the DATA hunk '
                             'at the first poll of every N-th one - the port\'s --dump checkpoints; needs --dump-from')
    parser.add_argument('--replay', metavar='LOG',
                        help='drive the run by a replay log (port/main.c format): inputs at their poll frames, '
                             'its seeds pinned at seed_random - one log for the original, a build and the port')
    parser.add_argument('--rng-record', action='store_true',
                        help='log every reseed of the game RNG (rng-reseeds.json); needs state dumps')
    parser.add_argument('--rng-pin', metavar='RUN',
                        help='write the seeds recorded by RUN at the same reseeds (needs state dumps)')
    args = parser.parse_args()
    INPUT = args.input; INPUT_OFFSET = args.input_offset; DUMP_FROM = args.dump_from; DUMP_EVERY = args.dump_every
    GAME_DIR = args.game_dir.resolve(); RUN = ROOT / 'build' / 'trace' / args.run_name; FRAMES = args.frames
    ORIGINAL = args.original; FLOPPY_SPEED = 0 if args.turbo_floppy else 100
    SHOT_FROM = args.screenshot_from; SHOT_EVERY = args.screenshot_every
    if args.poll_dumps:
        if DUMP_FROM is None:
            parser.error('--poll-dumps needs --dump-from (the frame from which the program is looked for)')
        POLLS = PollFrames(args.poll_dumps)
    if args.replay:
        if not args.poll_dumps:
            parser.error('--replay needs --poll-dumps: its inputs are timed in poll frames')
        REPLAY, replay_seeds = replay_events(args.replay)
        INPUT = str(ROOT / 'build' / 'trace' / 'empty-input.json')
        Path(INPUT).write_text('[]\n', encoding='utf-8')
    if args.rng_record or args.rng_pin or args.replay:
        if not (DUMP_EVERY or args.poll_dumps) or DUMP_FROM is None:
            parser.error('--rng-record/--rng-pin need --dump-from and --dump-every or --poll-dumps (the DATA hunk is located there)')
        from game_compare import map_offsets
        offset = RNG_STATE_OFFSET if ORIGINAL else map_offsets(GAME_DIR / 'DuckTales.sym', 0)['_G_h01_%04X' % RNG_STATE_OFFSET]
        pinned = (json.loads((ROOT / 'build' / 'trace' / args.rng_pin / 'rng-reseeds.json').read_text())['events']
                  if args.rng_pin else [dict(value=v) for v in replay_seeds] if args.replay else None)
        RNG = RngPin(offset, pinned)
    if args.action in ('prepare','run'): prepare()
    if args.action in ('boot','run'): boot()
