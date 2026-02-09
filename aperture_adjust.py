#!/usr/bin/env python3
"""
Aperture Adjustment Utility

Displays a side-by-side stream from two e3Vision cameras with mean pixel
intensity overlays to aid in manual aperture adjustment.

Usage:
    python aperture_adjust.py <reference_serial> <adjustment_serial>
"""

import argparse
import sys

import cv2
import numpy as np

# Configuration
WATCHTOWER_URL = "https://localhost:4343"
STREAM_RATE = 15
CENTER_REGION_PCT = 0.2


def build_stream_url(serial: str) -> str:
    """Build the MJPEG stream URL for a camera."""
    return f"{WATCHTOWER_URL}/cameras/{serial}/stream?fps={STREAM_RATE}"


def extract_center_region(frame: np.ndarray, pct: float) -> np.ndarray:
    """Extract the center region of a frame."""
    h, w = frame.shape[:2]
    region_h = int(h * pct)
    region_w = int(w * pct)
    y_start = (h - region_h) // 2
    x_start = (w - region_w) // 2
    return frame[y_start : y_start + region_h, x_start : x_start + region_w]


def calculate_mean_intensity(region: np.ndarray) -> float:
    """Convert region to grayscale and calculate mean intensity."""
    if len(region.shape) == 3:
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    else:
        gray = region
    return float(np.mean(gray))


def overlay_intensity(frame: np.ndarray, intensity: float, label: str) -> np.ndarray:
    """Overlay intensity value and label on frame."""
    frame = frame.copy()
    h, w = frame.shape[:2]

    # Draw label at top
    cv2.putText(
        frame,
        label,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Draw intensity value
    text = f"Intensity: {intensity:.1f}"
    cv2.putText(
        frame,
        text,
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    # Draw center region rectangle
    region_h = int(h * CENTER_REGION_PCT)
    region_w = int(w * CENTER_REGION_PCT)
    y_start = (h - region_h) // 2
    x_start = (w - region_w) // 2
    cv2.rectangle(
        frame,
        (x_start, y_start),
        (x_start + region_w, y_start + region_h),
        (0, 255, 0),
        2,
    )

    return frame


def main():
    parser = argparse.ArgumentParser(
        description="Display side-by-side camera streams with intensity overlay"
    )
    parser.add_argument("reference_serial", help="Serial number of reference camera")
    parser.add_argument("adjustment_serial", help="Serial number of camera to adjust")
    args = parser.parse_args()

    ref_url = build_stream_url(args.reference_serial)
    adj_url = build_stream_url(args.adjustment_serial)

    print(f"Opening reference camera stream: {args.reference_serial}")
    ref_cap = cv2.VideoCapture(ref_url)

    print(f"Opening adjustment camera stream: {args.adjustment_serial}")
    adj_cap = cv2.VideoCapture(adj_url)

    if not ref_cap.isOpened():
        print(f"Error: Could not open reference camera stream", file=sys.stderr)
        sys.exit(1)

    if not adj_cap.isOpened():
        print(f"Error: Could not open adjustment camera stream", file=sys.stderr)
        ref_cap.release()
        sys.exit(1)

    print("Streams opened. Press 'q' to quit.")

    try:
        while True:
            ref_ret, ref_frame = ref_cap.read()
            adj_ret, adj_frame = adj_cap.read()

            if not ref_ret or not adj_ret:
                print("Error reading from camera stream", file=sys.stderr)
                break

            # Calculate intensities from center regions
            ref_region = extract_center_region(ref_frame, CENTER_REGION_PCT)
            adj_region = extract_center_region(adj_frame, CENTER_REGION_PCT)

            ref_intensity = calculate_mean_intensity(ref_region)
            adj_intensity = calculate_mean_intensity(adj_region)

            # Overlay information on frames
            ref_display = overlay_intensity(
                ref_frame, ref_intensity, f"Reference: {args.reference_serial}"
            )
            adj_display = overlay_intensity(
                adj_frame, adj_intensity, f"Adjust: {args.adjustment_serial}"
            )

            # Resize frames to match heights if needed
            if ref_display.shape[0] != adj_display.shape[0]:
                target_h = min(ref_display.shape[0], adj_display.shape[0])
                ref_display = cv2.resize(
                    ref_display,
                    (
                        int(ref_display.shape[1] * target_h / ref_display.shape[0]),
                        target_h,
                    ),
                )
                adj_display = cv2.resize(
                    adj_display,
                    (
                        int(adj_display.shape[1] * target_h / adj_display.shape[0]),
                        target_h,
                    ),
                )

            # Concatenate horizontally
            combined = np.hstack([ref_display, adj_display])

            cv2.imshow("Aperture Adjustment", combined)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        ref_cap.release()
        adj_cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
