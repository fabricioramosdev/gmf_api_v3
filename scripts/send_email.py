import argparse
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
import mimetypes
from typing import Optional, List

try:
    # python-dotenv is in requirements; load if available
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def strtobool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def build_message(
    *,
    mail_from: str,
    mail_from_name: Optional[str],
    to: List[str],
    cc: Optional[List[str]],
    bcc: Optional[List[str]],
    subject: str,
    text: Optional[str],
    html: Optional[str],
    attachments: Optional[List[Path]],
) -> EmailMessage:
    msg = EmailMessage()
    if mail_from_name:
        msg["From"] = f"{mail_from_name} <{mail_from}>"
    else:
        msg["From"] = mail_from
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject

    # Content
    if html and text:
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")
    elif html:
        # derive minimal plain text fallback
        fallback = (html.replace("<br>", "\n")
                         .replace("<br/>", "\n")
                         .replace("<br />", "\n"))
        fallback = fallback
        msg.set_content(fallback)
        msg.add_alternative(html, subtype="html")
    elif text:
        msg.set_content(text)
    else:
        raise ValueError("Either --text or --html content must be provided")

    # Attachments
    for p in attachments or []:
        p = Path(p)
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"Attachment not found: {p}")
        ctype, encoding = mimetypes.guess_type(p.name)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(p, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=p.name)

    # Bcc not set as header; included only in recipients list
    return msg


def send_via_smtp(
    *,
    host: str,
    port: int,
    user: Optional[str],
    password: Optional[str],
    use_ssl: bool,
    use_tls: bool,
    msg: EmailMessage,
    from_addr: str,
    to_addrs: List[str],
    timeout: int = 30,
    debug: bool = False,
) -> None:
    if use_ssl:
        server = smtplib.SMTP_SSL(host, port, timeout=timeout, context=ssl.create_default_context())
    else:
        server = smtplib.SMTP(host, port, timeout=timeout)
    try:
        if debug:
            server.set_debuglevel(1)
        if not use_ssl and use_tls:
            server.starttls(context=ssl.create_default_context())
        if user:
            server.login(user, password or "")
        server.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)
    finally:
        try:
            server.quit()
        except Exception:
            server.close()


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Send an email via SMTP using env/CLI config")
    p.add_argument("--to", "-t", nargs="+", required=True, help="Recipient email(s)")
    p.add_argument("--cc", nargs="*", help="CC email(s)")
    p.add_argument("--bcc", nargs="*", help="BCC email(s)")
    p.add_argument("--subject", "-s", required=True, help="Email subject")
    content = p.add_mutually_exclusive_group(required=False)
    content.add_argument("--text", help="Plain text body")
    content.add_argument("--html", help="HTML body")
    p.add_argument("--text-file", help="Path to file containing plain text body")
    p.add_argument("--html-file", help="Path to file containing HTML body")
    p.add_argument("--attach", nargs="*", default=[], help="Attachment file path(s)")
    p.add_argument("--from", dest="from_email", help="Override MAIL_FROM env")
    p.add_argument("--from-name", dest="from_name", help="Override MAIL_FROM_NAME env")
    p.add_argument("--host", help="Override SMTP_HOST env")
    p.add_argument("--port", type=int, help="Override SMTP_PORT env")
    p.add_argument("--user", help="Override SMTP_USER env")
    p.add_argument("--password", help="Override SMTP_PASSWORD env")
    p.add_argument("--ssl", action="store_true", help="Force SSL (SMTPS)")
    p.add_argument("--tls", action="store_true", help="Force STARTTLS")
    p.add_argument("--no-tls", action="store_true", help="Disable STARTTLS even if env enabled")
    p.add_argument("--dry-run", action="store_true", help="Do not send, just print summary")
    p.add_argument("--debug", action="store_true", help="Enable SMTP debug output")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    # Resolve content from args or files
    text = args.text
    html = args.html
    if args.text_file:
        try:
            text = Path(args.text_file).read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading --text-file: {e}", file=sys.stderr)
            return 2
    if args.html_file:
        try:
            html = Path(args.html_file).read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading --html-file: {e}", file=sys.stderr)
            return 2

    if not (text or html):
        print("Provide --text/--html or --text-file/--html-file", file=sys.stderr)
        return 2

    # SMTP config from env with CLI overrides
    host = args.host or os.getenv("SMTP_HOST", "smtp.gmail.com")
    use_ssl = args.ssl or strtobool(os.getenv("SMTP_USE_SSL"), default=False)
    use_tls_env = strtobool(os.getenv("SMTP_USE_TLS"), default=True)
    use_tls = args.tls or (use_tls_env and not args.no_tls)
    # sensible default ports
    default_port = 465 if use_ssl else (587 if use_tls else 25)
    port = args.port or int(os.getenv("SMTP_PORT", default_port))
    user = args.user or os.getenv("SMTP_USER")
    password = args.password or os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS")
    from_email = args.from_email or os.getenv("MAIL_FROM") or user
    from_name = args.from_name or os.getenv("MAIL_FROM_NAME")

    if not host:
        print("SMTP_HOST is required (via env or --host)", file=sys.stderr)
        return 2
    if not from_email:
        print("MAIL_FROM or --from is required (or set SMTP_USER)", file=sys.stderr)
        return 2

    # Build message
    try:
        msg = build_message(
            mail_from=from_email,
            mail_from_name=from_name,
            to=args.to,
            cc=args.cc,
            bcc=args.bcc,
            subject=args.subject,
            text=text,
            html=html,
            attachments=[Path(a) for a in (args.attach or [])],
        )
    except Exception as e:
        print(f"Error building message: {e}", file=sys.stderr)
        return 2

    recipients = list(args.to or []) + list(args.cc or []) + list(args.bcc or [])
    if not recipients:
        print("At least one recipient is required", file=sys.stderr)
        return 2

    if args.dry_run:
        print("[DRY RUN] Would send email with:")
        print(f"  From: {msg['From']}")
        print(f"  To: {msg.get('To')}")
        if msg.get('Cc'):
            print(f"  Cc: {msg.get('Cc')}")
        print(f"  Subject: {msg.get('Subject')}")
        print(f"  Attachments: {len([p for p in (args.attach or [])])}")
        return 0

    try:
        send_via_smtp(
            host=host,
            port=port,
            user=user,
            password=password,
            use_ssl=use_ssl,
            use_tls=use_tls,
            msg=msg,
            from_addr=from_email,
            to_addrs=recipients,
            debug=args.debug,
        )
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP auth failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)
        return 1

    print("Email sent successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
