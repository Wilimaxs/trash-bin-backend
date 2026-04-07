from datetime import timedelta

def is_idle_timeout(last_activity, current_time, timeout_minutes=5) -> bool:
    """
    Mengecek apakah durasi idle sudah melebihi batas timeout_minutes.
    Secara otomatis mensinkronkan offset-naive dan offset-aware realtime.
    """
    if not last_activity:
        return False
        
    if last_activity.tzinfo is None and current_time.tzinfo is not None:
        last_activity = last_activity.replace(tzinfo=current_time.tzinfo)
    elif last_activity.tzinfo is not None and current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=last_activity.tzinfo)
        
    time_diff = current_time - last_activity
    return time_diff > timedelta(minutes=timeout_minutes)

