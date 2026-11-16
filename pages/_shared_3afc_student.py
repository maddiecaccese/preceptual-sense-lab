"""Shared TODOs for all 3AFC assignment pages.

Why this file exists:
- All 3AFC pages use the same staircase, accuracy, and plotting patterns.
- Shared logic is implemented here once and reused by all 3AFC pages.

Used by:
- pages/sound_gap_detection.py
- pages/amplitude_threshold.py
- pages/pitch_threshold.py

Implementation expectations:
- Keep return types exactly as annotated.
- Prefer small, pure functions with no Streamlit state mutations.
- Validate/clamp values to avoid invalid outputs.
"""
import matplotlib.pyplot as plt
import streamlit as st

def shared_student_apply_reversal_update(
    *,
    current_level: float,
    step: float,
    is_correct: bool,
    correct_streak: int,
    down_n: int,
    min_level: float,
    max_level: float,
) -> tuple[float, int]:
    """Apply one 2-down/1-up staircase update.

    Inputs:
        current_level: current adaptive stimulus level.
        step: step size for level change.
        is_correct: whether the response is correct.
        correct_streak: consecutive correct count before this trial.
        down_n: number of correct responses needed to step down.
        min_level: minimum allowed level.
        max_level: maximum allowed level.

    Returns:
        Tuple `(next_level, next_correct_streak)` after one update.

    Safety requirements:
        - Clamp level to `[min_level, max_level]`.
        - Treat `down_n < 1` as 1 to avoid zero-step loops.
    """
    if not is_correct:
        current_level = current_level + step
        correct_streak = 0
    else:
        correct_streak += 1
        if down_n < 1:
            down_n = 1
        if correct_streak >= down_n:
            #met correct number of responses to get harder question
            current_level = current_level - step
            correct_streak = 0 # need to set to 0 so that we count for next streak after step down
        #else not enough correct yet to get harder question
    current_level = min(max_level, current_level) #ensure to stay above min range
    current_level = max(min_level, current_level) #ensure to stay below max range
    return (current_level, correct_streak)

def shared_student_plot_staircase(
    history: list[dict], threshold: float, y_label: str, title: str
) -> None:
    """Plot the staircase trace for the given history.

    Expected plot content:
        - X-axis: trial number.
        - Y-axis: level value per trial.
        - Visual distinction for correct vs incorrect trials.
        - Threshold drawn as a horizontal dashed line.

    Safety requirements:
        - Do not crash for empty or very short history lists.
    """
    x = range(len(history))
    print(x)
    y= []
    for metric in history:
        y.append(metric["Correct"])
    fig, ax = plt.subplots()
    ax.step(x, y, where="post", label="Step", linewidth=2)
    ax.axhline(y=threshold, color="red", label="Threshold", linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("Trial Number")
    ax.set_ylabel(y_label)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    st.pyplot(fig)

def shared_student_build_three_interval_targets(*, target_index: int) -> list[bool]:
    """Build a length-3 target mask with exactly one `True` entry.

    Example:
        target_index=1 -> [False, True, False]
    """
    result = []
    for index in range(3):
        if index == target_index:
            result.append(True)
        else:
            result.append(False)
    return result

def shared_student_update_staircase_state(
    *,
    current_level: float,
    step: float,
    is_correct: bool,
    correct_streak: int,
    down_n: int,
    min_level: float,
    max_level: float,
) -> tuple[float, int]:
    """Reusable helper that keeps staircase behavior consistent.

    This can wrap or share logic with `shared_student_apply_reversal_update`.
    """
    return shared_student_apply_reversal_update(current_level=current_level, step=step, is_correct=is_correct, correct_streak=correct_streak, down_n=down_n, min_level=min_level, max_level=max_level)

def shared_student_estimate_threshold_from_reversals(
    *, reversals: list[float], fallback_level: float, tail_count: int = 4
) -> float:
    """Estimate threshold using the trailing reversal points.

    Recommended behavior:
        - When there are enough reversals, average the last `tail_count` values.
        - Otherwise return `fallback_level`.
    """
    if len(reversals) >= tail_count:
        return sum(reversals[-4:]) / len(reversals[-4:])
    else:
        return fallback_level

def shared_student_compute_recent_accuracy(history: list[dict], window: int = 12) -> float:
    """Compute a trailing percent-correct accuracy metric.

    Output should be a percentage in the `[0, 100]` range.
    """
    accuracy_list = []
    for metric in history:
        if metric["Correct"] == "Yes":
            accuracy_list.append(1)
        else:
            accuracy_list.append(0)
    trailing_accuracy: float = (sum(accuracy_list[-window:]) / len(accuracy_list[-window:])) * 100
    return trailing_accuracy


def shared_student_validate_audio_params(*, amplitude: float, stimulus_value: float) -> bool:
    """Validate amplitude and stimulus-specific numeric values.

    Returns:
        `True` when inputs are in safe ranges, otherwise `False`.
    """
    #researched and safe amplitudes are between 0.0001 and 0.5
    # safe stimulus value is
    if amplitude > 0.5 or amplitude < 0.0001 or stimulus_value <= 0:
        return False
    else:
        return True


def shared_student_plot_staircase_with_threshold(
    *, history: list[dict], threshold: float, y_label: str, title: str
) -> None:
    """Wrapper that draws the staircase and highlights the threshold.

    Hint:
        Call `shared_student_plot_staircase(...)` internally to avoid duplicate code.
    """
    shared_student_plot_staircase(history, threshold, y_label, title)