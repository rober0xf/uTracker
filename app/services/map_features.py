def to_float(value):
    if isinstance(value, str):
        return float(value.strip("%").split()[0])
    return float(value) if value else 0.0


def map_api_to_features(api_data):
    records = api_data.get("Records", {})
    win_stats = api_data.get("Win Stats", {})

    return {
        "avg_sig_str_landed": to_float(records.get("Sig. Str. Landed")),
        "avg_sig_str_pct": to_float(records.get("Striking accuracy")),
        "avg_sub_att": to_float(records.get("Submission avg")),
        "avg_td_landed": to_float(records.get("Takedown avg")),
        "avg_td_pct": to_float(records.get("Takedown Accuracy")),
        "wins_by_ko": int(win_stats.get("Wins by Knockout", 0)),
        "wins_by_submission": int(win_stats.get("Wins by Submission", 0)),
    }
