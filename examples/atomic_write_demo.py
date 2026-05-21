from pathlib import Path
import tempfile

from support_api.utils import atomic_write

with tempfile.TemporaryDirectory() as tempdir:
    target = Path(tempdir) / "demo.txt"
    target.write_text("ORIGINAL")
    print(f"The original file: {target.read_text()}")

    # Happy Path: contents get replaced
    with atomic_write(target) as file:
        file.write("NEW CONTENTS")
    print(f"After happy path: {target.read_text()}")

    leftoverSuccess = target.with_suffix(".txt.tmp")
    print(f"Tempfile left behind: {leftoverSuccess.exists()}")

    # Failure Path: target is NOT changed
    try:
        with atomic_write(target) as file:
            file.write("WOULD-BE REPLACEMENT")
            raise RuntimeError("boom, get wrkt")
    except RuntimeError:
        print(f"After failure path: {target.read_text()}")


    leftoverFailure = target.with_suffix(".txt.tmp")
    print(f"Tempfile left behind: {leftoverFailure.exists()}")