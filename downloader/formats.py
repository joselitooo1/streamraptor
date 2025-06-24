def extract_format_options(formats):
    results = []
    for f in formats:
        if f.get("vcodec") != "none":
            size = f.get("filesize") or f.get("filesize_approx") or 0
            readable = f"{round(size / 1024 / 1024, 2)} MB" if size else "taille inconnue"
            label = f"{f.get('format_note', '')} - {f.get('ext', '')} - {readable}"
            results.append({"id": f["format_id"], "label": label})
    return results
