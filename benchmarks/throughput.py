import argparse
import csv
import secrets
import shutil
import sys
import time
from pathlib import Path


try:
    from mrhscrypto import MRHSCrypto
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    from mrhscrypto import MRHSCrypto


def time_call(function):
    started_at = time.perf_counter()
    result = function()
    elapsed = time.perf_counter() - started_at
    return result, elapsed


def format_seconds(seconds):
    if seconds is None:
        return ""
    return f"{seconds:.9f}"


def key_memory_sizes(keypair):
    public_key_bytes = keypair.public_key.G.nbytes
    private_key_bytes = keypair.private_key.M.nbytes + keypair.private_key.R.nbytes
    public_key_theoretical_bytes = public_key_bytes // 8
    private_key_theoretical_bytes = private_key_bytes // 8
    public_key_object_bytes = (
        sys.getsizeof(keypair.public_key)
        + sys.getsizeof(keypair.public_key.parameters)
        + sys.getsizeof(keypair.public_key.G)
    )
    private_key_object_bytes = (
        sys.getsizeof(keypair.private_key)
        + sys.getsizeof(keypair.private_key.parameters)
        + sys.getsizeof(keypair.private_key.M)
        + sys.getsizeof(keypair.private_key.R)
    )
    return {
        "public_key_memory_bytes": public_key_bytes,
        "private_key_memory_bytes": private_key_bytes,
        "keypair_memory_bytes": public_key_bytes + private_key_bytes,
        "public_key_theoretical_bytes": public_key_theoretical_bytes,
        "private_key_theoretical_bytes": private_key_theoretical_bytes,
        "keypair_theoretical_bytes": public_key_theoretical_bytes
        + private_key_theoretical_bytes,
        "public_key_object_bytes": public_key_object_bytes,
        "private_key_object_bytes": private_key_object_bytes,
        "keypair_object_bytes": public_key_object_bytes + private_key_object_bytes,
    }


def key_file_sizes(keypair, directory, trial):
    public_key_path = directory / f"public_key_{trial}.npz"
    private_key_path = directory / f"private_key_{trial}.npz"

    keypair.public_key.save(public_key_path)
    keypair.private_key.save(private_key_path)

    public_key_bytes = public_key_path.stat().st_size
    private_key_bytes = private_key_path.stat().st_size

    public_key_path.unlink()
    private_key_path.unlink()

    return public_key_bytes, private_key_bytes, public_key_bytes + private_key_bytes


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def result_path(results_dir, name, suffix):
    return results_dir / f"{name}{suffix}.csv"


def ops_per_second(rows, column):
    times = [float(row[column]) for row in rows if row.get(column)]
    if not times:
        return 0.0
    return len(times) / sum(times)


def times_from_rows(rows, column):
    return [float(row[column]) for row in rows if row.get(column)]


def percentile(values, percent):
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * percent)
    return sorted_values[index]


def median(values):
    return percentile(values, 0.5)


def trimmed_ops_per_second(values, trim=0.01):
    if not values:
        return 0.0
    sorted_values = sorted(values)
    start = int(len(sorted_values) * trim)
    end = int(len(sorted_values) * (1 - trim))
    trimmed = sorted_values[start:end]
    if not trimmed:
        return 0.0
    return len(trimmed) / sum(trimmed)


def add_timing_summary(summary, prefix, rows, column):
    times = times_from_rows(rows, column)
    summary[f"{prefix}_per_second"] = f"{ops_per_second(rows, column):.6f}"
    summary[f"{prefix}_median_time_seconds"] = f"{median(times):.9f}"
    median_time = median(times)
    summary[f"{prefix}_median_ops_per_second"] = (
        f"{(1 / median_time) if median_time else 0.0:.6f}"
    )
    summary[f"{prefix}_p90_time_seconds"] = f"{percentile(times, 0.90):.9f}"
    summary[f"{prefix}_p95_time_seconds"] = f"{percentile(times, 0.95):.9f}"
    summary[f"{prefix}_p99_time_seconds"] = f"{percentile(times, 0.99):.9f}"
    summary[f"{prefix}_max_time_seconds"] = f"{max(times) if times else 0.0:.9f}"
    summary[f"{prefix}_trimmed_1_percent_ops_per_second"] = (
        f"{trimmed_ops_per_second(times):.6f}"
    )


def average(values):
    return sum(values) / len(values) if values else 0.0


def min_value(values):
    return min(values) if values else 0


def max_value(values):
    return max(values) if values else 0


def print_progress(trial, total, started_at):
    elapsed = time.perf_counter() - started_at
    done_fraction = trial / total
    remaining = (elapsed / done_fraction) - elapsed if done_fraction else 0.0
    percent = done_fraction * 100
    print(
        f"Trial {trial}/{total} ({percent:.1f}%) | "
        f"elapsed {elapsed:.1f}s | remaining ~{remaining:.1f}s",
        flush=True,
    )


def build_summary(security, c2_label, keygen_rows, encrypt_rows, decrypt_rows):
    public_key_npz_sizes = [int(row["public_key_npz_bytes"]) for row in keygen_rows]
    private_key_npz_sizes = [int(row["private_key_npz_bytes"]) for row in keygen_rows]
    keypair_npz_sizes = [int(row["keypair_npz_bytes"]) for row in keygen_rows]
    ciphertext_sizes = [int(row["ciphertext_bytes"]) for row in encrypt_rows]
    decrypt_successes = sum(1 for row in decrypt_rows if row["time_seconds"])
    decrypt_errors = sum(1 for row in decrypt_rows if row["error"])

    summary = {
        "lambda": security,
        "c2": c2_label,
        "trials": len(keygen_rows),
        "decrypt_successes": decrypt_successes,
        "decrypt_errors": decrypt_errors,
        "public_key_theoretical_bytes": keygen_rows[0][
            "public_key_theoretical_bytes"
        ],
        "private_key_theoretical_bytes": keygen_rows[0][
            "private_key_theoretical_bytes"
        ],
        "keypair_theoretical_bytes": keygen_rows[0]["keypair_theoretical_bytes"],
        "public_key_memory_bytes": keygen_rows[0]["public_key_memory_bytes"],
        "private_key_memory_bytes": keygen_rows[0]["private_key_memory_bytes"],
        "keypair_memory_bytes": keygen_rows[0]["keypair_memory_bytes"],
        "public_key_object_bytes": keygen_rows[0]["public_key_object_bytes"],
        "private_key_object_bytes": keygen_rows[0]["private_key_object_bytes"],
        "keypair_object_bytes": keygen_rows[0]["keypair_object_bytes"],
        "public_key_npz_bytes_avg": f"{average(public_key_npz_sizes):.2f}",
        "public_key_npz_bytes_min": min_value(public_key_npz_sizes),
        "public_key_npz_bytes_max": max_value(public_key_npz_sizes),
        "private_key_npz_bytes_avg": f"{average(private_key_npz_sizes):.2f}",
        "private_key_npz_bytes_min": min_value(private_key_npz_sizes),
        "private_key_npz_bytes_max": max_value(private_key_npz_sizes),
        "keypair_npz_bytes_avg": f"{average(keypair_npz_sizes):.2f}",
        "keypair_npz_bytes_min": min_value(keypair_npz_sizes),
        "keypair_npz_bytes_max": max_value(keypair_npz_sizes),
        "ciphertext_bytes_avg": f"{average(ciphertext_sizes):.2f}",
        "ciphertext_bytes_min": min_value(ciphertext_sizes),
        "ciphertext_bytes_max": max_value(ciphertext_sizes),
    }
    add_timing_summary(summary, "keygen", keygen_rows, "time_seconds")
    add_timing_summary(summary, "encrypt", encrypt_rows, "time_seconds")
    add_timing_summary(summary, "decrypt", decrypt_rows, "time_seconds")
    return [summary]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run MRHScrypto per-trial keygen, encrypt, and decrypt benchmarks."
    )
    parser.add_argument("--lambda", dest="security", type=int, choices=(128, 256), default=128)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("benchmarks/results"),
    )
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=50,
        help="Print progress after this many trials.",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Suffix added to output file names, for example _128 or _256.",
    )
    parser.add_argument(
        "--c2-label",
        default="",
        help="Recorded c2 value label for the summary CSV.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    message_size = args.security // 8
    keygen_rows = []
    encrypt_rows = []
    decrypt_rows = []
    temp_dir = args.results_dir / "tmp_key_sizes"
    started_at = time.perf_counter()

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    try:
        for trial in range(1, args.iterations + 1):
            keypair, keygen_time = time_call(
                lambda: MRHSCrypto.generate_keypair(d=1, security=args.security)
            )

            key_sizes = key_memory_sizes(keypair)
            (
                public_key_npz_bytes,
                private_key_npz_bytes,
                keypair_npz_bytes,
            ) = key_file_sizes(keypair, temp_dir, trial)

            keygen_rows.append(
                {
                    "try": trial,
                    "lambda": args.security,
                    "c2": args.c2_label,
                    "time_seconds": format_seconds(keygen_time),
                    **key_sizes,
                    "public_key_npz_bytes": public_key_npz_bytes,
                    "private_key_npz_bytes": private_key_npz_bytes,
                    "keypair_npz_bytes": keypair_npz_bytes,
                }
            )

            message = secrets.token_bytes(message_size)
            encryptor = MRHSCrypto.new(keypair.public_key)
            ciphertext, encrypt_time = time_call(lambda: encryptor.encrypt(message))
            encrypt_rows.append(
                {
                    "try": trial,
                    "lambda": args.security,
                    "c2": args.c2_label,
                    "time_seconds": format_seconds(encrypt_time),
                    "ciphertext_bytes": len(ciphertext),
                }
            )

            decrypt_time = None
            decrypt_error = ""
            decryptor = MRHSCrypto.new(keypair.private_key)
            try:
                decrypted, decrypt_time = time_call(lambda: decryptor.decrypt(ciphertext))
                if decrypted != message:
                    raise RuntimeError("decrypted message does not match original message")
            except Exception as exc:
                decrypt_time = None
                decrypt_error = f"{type(exc).__name__}: {exc}"

            decrypt_rows.append(
                {
                    "try": trial,
                    "lambda": args.security,
                    "c2": args.c2_label,
                    "time_seconds": format_seconds(decrypt_time),
                    "error": decrypt_error,
                }
            )

            if (
                trial == 1
                or trial % args.progress_interval == 0
                or trial == args.iterations
            ):
                print_progress(trial, args.iterations, started_at)
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    write_csv(
        result_path(args.results_dir, "keygen", args.suffix),
        [
            "try",
            "lambda",
            "c2",
            "time_seconds",
            "public_key_theoretical_bytes",
            "private_key_theoretical_bytes",
            "keypair_theoretical_bytes",
            "public_key_memory_bytes",
            "private_key_memory_bytes",
            "keypair_memory_bytes",
            "public_key_object_bytes",
            "private_key_object_bytes",
            "keypair_object_bytes",
            "public_key_npz_bytes",
            "private_key_npz_bytes",
            "keypair_npz_bytes",
        ],
        keygen_rows,
    )
    write_csv(
        result_path(args.results_dir, "encrypt", args.suffix),
        ["try", "lambda", "c2", "time_seconds", "ciphertext_bytes"],
        encrypt_rows,
    )
    write_csv(
        result_path(args.results_dir, "decrypt", args.suffix),
        ["try", "lambda", "c2", "time_seconds", "error"],
        decrypt_rows,
    )
    summary_rows = build_summary(
        args.security, args.c2_label, keygen_rows, encrypt_rows, decrypt_rows
    )
    write_csv(
        result_path(args.results_dir, "summary", args.suffix),
        list(summary_rows[0].keys()),
        summary_rows,
    )

    summary = summary_rows[0]
    print()
    print("Results")
    print("=======")
    print(f"keygen : {summary['keygen_per_second']} ops/s")
    print(f"encrypt: {summary['encrypt_per_second']} ops/s")
    print(f"decrypt: {summary['decrypt_per_second']} ops/s")
    print(f"decrypt errors: {summary['decrypt_errors']}")
    print(f"CSV files written to: {args.results_dir}")


if __name__ == "__main__":
    main()
