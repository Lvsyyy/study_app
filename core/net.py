"""Shared helpers for outbound HTTPS requests."""
import ssl
import subprocess
import sys


def ssl_context():
    """Build a verified TLS context using certifi or macOS system roots."""
    try:
        import certifi
    except ImportError:
        certifi = None

    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())

    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                [
                    "/usr/bin/security",
                    "find-certificate",
                    "-a",
                    "-p",
                    "/System/Library/Keychains/SystemRootCertificates.keychain",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            result = None
        if result is not None and result.stdout.strip():
            return ssl.create_default_context(cadata=result.stdout)

    return ssl.create_default_context()
