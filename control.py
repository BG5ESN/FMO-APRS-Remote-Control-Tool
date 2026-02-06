#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import hmac
import json
import socket
import sys
import time
from pathlib import Path

DEFAULT_HOST = "china.aprs2.net"
DEFAULT_PORT = 14580
DEFAULT_DEVICE = "APFMO0"  # FMO_DEVICE_APRS_TO_CALLSIGN_EXCHANGE
DEFAULT_PATH = "TCPIP*"


def parse_callsign_ssid(callsign_ssid: str):
    s = callsign_ssid.strip().upper()
    if not s:
        raise ValueError("callsign is empty")
    if "-" in s:
        call, ssid_str = s.split("-", 1)
        if not call:
            raise ValueError("callsign missing before '-'")
        if not ssid_str.isdigit():
            raise ValueError("SSID must be number")
        ssid = int(ssid_str)
    else:
        call = s
        ssid = 0
    if ssid < 0 or ssid > 15:
        raise ValueError("SSID out of range (0~15)")
    return call, ssid


def format_addressee(to_call: str, to_ssid: int) -> str:
    if to_ssid and to_ssid != 0:
        addr = f"{to_call}-{to_ssid}"
    else:
        addr = to_call
    if len(addr) > 9:
        raise ValueError(f"TO addressee too long: {addr}")
    return addr.ljust(9, " ")


def calc_signature(from_call: str,
                   from_ssid: int,
                   type_str: str,
                   action_str: str,
                   time_slot: int,
                   counter: int,
                   secret: str) -> str:
    # 注意：固件端实现为字段直接拼接，不包含分隔符。
    # SIGNATURE = HMAC-SHA1(key=SECRET, msg=CALL+SSID+TYPE+ACTION+T+C)
    raw = (
        f"{from_call}"
        f"{from_ssid}"
        f"{type_str}"
        f"{action_str}"
        f"{time_slot}"
        f"{counter}"
    )
    digest = hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha1).digest()
    return digest[:8].hex().upper()


def load_state(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: Path, state: dict):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def next_counter(state_path: Path, time_slot: int) -> int:
    st = load_state(state_path)
    last_ts = st.get("time_slot")
    last_c = st.get("counter")
    if isinstance(last_ts, int) and isinstance(last_c, int) and last_ts == time_slot:
        c = last_c + 1
    else:
        c = 0
    st["time_slot"] = time_slot
    st["counter"] = c
    save_state(state_path, st)
    return c


def connect(host: str, port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((host, port))
    s.settimeout(None)
    return s


def send_line(sock: socket.socket, line: str):
    if not line.endswith("\n"):
        line += "\n"
    sock.sendall(line.encode("utf-8"))


def recv_lines(sock: socket.socket, timeout_sec: float):
    sock.settimeout(0.5)
    end = time.time() + timeout_sec
    buf = b""
    while time.time() < end:
        try:
            data = sock.recv(4096)
        except socket.timeout:
            continue
        if not data:
            break
        buf += data
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            text = line.decode(errors="ignore").strip("\r")
            if text.strip():
                yield text


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="FMO APRS Remote Control sender (ARCP).\n"
                    "示例: python control.py BG5ESN-11 22446 SECRET STANDBY",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument("mycall", help="登录呼号(含SSID), 如 BG5ESN-11")
    ap.add_argument("passcode", help="APRS-IS passcode, 如 22446")
    ap.add_argument("secret", help="设备端预共享密钥 SECRET")
    ap.add_argument("action", help="动作: NORMAL/STANDBY/REBOOT (大小写不敏感)")
    ap.add_argument("--to", dest="to_call", default=None, help="目标呼号(含SSID). 缺省=同mycall")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", default=DEFAULT_PORT, type=int)
    ap.add_argument("--device", default=DEFAULT_DEVICE, help="APRS device 字段(缺省 APFMO0)")
    ap.add_argument("--wait", default=6.0, type=float, help="等待ACK秒数")
    ap.add_argument("--counter", default=None, type=int, help="手动指定C(不指定则自动递增)")
    args = ap.parse_args(argv)

    from_call, from_ssid = parse_callsign_ssid(args.mycall)
    if args.to_call is None:
        to_call, to_ssid = from_call, from_ssid
    else:
        to_call, to_ssid = parse_callsign_ssid(args.to_call)

    action = args.action.strip().upper()

    if action not in ("NORMAL", "STANDBY", "REBOOT"):
        raise SystemExit(f"不支持的action: {action}")

    time_slot = int(time.time() // 60)
    state_path = Path(__file__).with_name("control_state.json")
    counter = args.counter if args.counter is not None else next_counter(state_path, time_slot)

    sig = calc_signature(
        from_call=from_call,
        from_ssid=from_ssid,
        type_str="CONTROL",
        action_str=action,
        time_slot=time_slot,
        counter=counter,
        secret=args.secret,
    )

    payload = f"CONTROL,{action},{time_slot},{counter},{sig}"

    addressee = format_addressee(to_call, to_ssid)
    raw = f"{from_call}-{from_ssid}>{args.device},{DEFAULT_PATH}::" \
          f"{addressee}:{payload}"

    print(f"[连接] {args.host}:{args.port}")
    sock = connect(args.host, args.port)
    try:
        login = f"user {from_call}-{from_ssid} pass {args.passcode} vers FMO-CTRL 0.1"
        print(f">> {login}")
        send_line(sock, login)
        time.sleep(0.3)

        print(f">> {raw}")
        send_line(sock, raw)

        if args.wait > 0:
            print(f"[等待ACK] {args.wait:.1f}s")
            for line in recv_lines(sock, args.wait):
                # ACK 是普通 MESSAGE，payload 会包含 :ACK,CONTROL,...
                if ":ACK,CONTROL," in line or "ACK,CONTROL," in line:
                    print(f"<< {line}")
            print("[结束]")
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()


if __name__ == "__main__":
    main()
