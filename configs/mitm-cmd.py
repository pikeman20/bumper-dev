"""MITM Proxy Script to capture and save unique traffic.

This script captures HTTP traffic, identifies unique commands based on their payloads,
counts how many times each one appears, and saves the results to a markdown file.
Sensitive information is anonymized.
"""  # noqa: INP001

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import threading
from typing import Any

from mitmproxy import ctx, http


@dataclass
class CmdName:
    """Represents a unique command interaction with request/response."""

    id: str
    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    count: int = 1


unique_traffic: dict[str, list[CmdName]] = {}
ignore_list: list[str] = []

_save_lock = threading.Lock()

# Optional periodic saving setup:
# _SAVE_INTERVAL_SECONDS = 10
# _save_thread_running = True
# def interval_writer():
#     while _save_thread_running:
#         time.sleep(_SAVE_INTERVAL_SECONDS)
#         _save_traffic()
# def load(l):
#     threading.Thread(target=interval_writer, daemon=True).start()


def done() -> None:
    """Write when mitmproxy session ends."""
    # global _save_thread_running
    # _save_thread_running = False
    _save_traffic()


def request(flow: http.HTTPFlow) -> None:
    """Handle HTTP request and track unique command request data."""
    try:
        cmd = _create_id(flow)
        if not cmd:
            return

        cmd_name, cmd_hash = cmd
        messages = unique_traffic.setdefault(cmd_name, [])

        # Check if we've seen this exact request before
        for entry in messages:
            if entry.id == cmd_hash:
                entry.count += 1
                return

        # New request - save it
        data = safe_json_load(flow.request.text, "request")
        if data is None:
            return
        data["query"] = dict(flow.request.query)
        messages.append(CmdName(id=cmd_hash, request=data))

    except Exception as e:
        ctx.log.error(f"Error handling request: {e}")


def response(flow: http.HTTPFlow) -> None:
    """Match the response to its request and attach the response body."""
    try:
        cmd = _create_id(flow)
        if not cmd:
            return

        cmd_name, cmd_hash = cmd
        for entry in unique_traffic.get(cmd_name, []):
            if entry.id == cmd_hash:
                entry.response = safe_json_load(flow.response.text, "response")
                _save_traffic()
                return

        ctx.log.warning(f"No matching request found for response: {cmd_hash}")
    except Exception as e:
        ctx.log.error(f"Error handling response: {e}")


def _create_id(flow: http.HTTPFlow) -> tuple[str, str] | None:
    """Create a unique ID based on the command name and payload hash."""
    try:
        request_data = safe_json_load(flow.request.text, "request")
        if request_data is None:
            return None
        request_data.update(dict(flow.request.query))
        command = request_data.get("cmdName") or request_data.get("apn")

        if not command or command in ignore_list:
            return None

        payload_id = _extract_payload_id(request_data)
        return (command, payload_id) if payload_id else None
    except Exception as e:
        ctx.log.error(f"Error parsing request: {e}")
    return None


def safe_json_load(text: str, context: str = "request") -> dict[str, Any] | None:
    """Safely parse JSON from text and log errors."""
    try:
        return json.loads(text) if text.strip() else None
    except json.JSONDecodeError as e:
        ctx.log.debug(f"[{context}] JSON decode error: {e} -- Raw: {text[:100]!r}")
    except Exception as e:
        ctx.log.debug(f"[{context}] Unexpected error: {e} -- Raw: {text[:100]!r}")
    return None


def _extract_payload_id(data: dict[str, Any]) -> str | None:
    """Create a stable hash of the command's body data for uniqueness."""
    version = 1 if "cmdName" in data else 2 if "apn" in data else None
    command = data.get("cmdName" if version == 1 else "apn")
    if not command or command in ignore_list:
        return None

    pay_b_d = None
    if version == 1:
        pay_b_d = data.get("payload", {}).get("body", {}).get("data")
        if isinstance(pay_b_d, dict):
            pay_b_d.pop("bdTaskID", None)
    else:
        pay_b_d = data.get("body", {}).get("data")

    if pay_b_d is not None:
        hash_str = hashlib.sha256(str(pay_b_d).encode("utf-8")).hexdigest()
        return f"{command}_{hash_str}"
    return None


def _save_traffic() -> None:
    """Write unique traffic to a markdown file."""
    try:
        with _save_lock:
            with Path("/mitm/unique_traffic.md").open("w", encoding="utf-8") as outfile:
                for cmd_name, messages in unique_traffic.items():
                    outfile.write("<details>\n")
                    outfile.write(f"  <summary>{cmd_name}</summary>\n\n")
                    outfile.write(f"![{cmd_name}]({cmd_name}.png)\n\n")
                    for msg in messages:
                        cleaned = _replace_sensitive_info(
                            {
                                "request": msg.request,
                                "response": msg.response,
                            },
                        )
                        outfile.write(f"**Seen:** {msg.count} times\n\n")
                        outfile.write("```json\n")
                        json.dump(cleaned, outfile, indent=2, ensure_ascii=False)
                        outfile.write("\n```\n\n")
                    outfile.write("</details>\n\n")
            ctx.log.info("Traffic saved to /mitm/unique_traffic.md")
    except Exception as e:
        ctx.log.error(f"Error during save: {e}")


def _replace_sensitive_info(data: dict[str, Any]) -> dict[str, Any]:
    """Strip or anonymize sensitive fields in the captured data."""
    request = data.get("request")
    possible_keys = ["eid", "er", "realm", "resource", "toId", "token", "toRes", "userid", "with", "did"]
    if request:
        for key in possible_keys:
            if key in request:
                request[key] = "REPLACED"
        if "auth" in request:
            for field in possible_keys:
                request["auth"][field] = "REPLACED"
        if "query" in request:
            for field in possible_keys:
                if field in request["query"]:
                    request["query"][field] = "REPLACED"

    response = data.get("response")
    if response and "id" in response:
        response["id"] = "REPLACED"

    return data
