def extract_icon(text_with_icon):

    if not text_with_icon:
        return ""
    common_icons = ["💵", "🏦", "💳", "🍔", "🧑‍🤝‍🧑", "🐶", "🚗", "🎭", "🏠", "👕", "💄", "🩺", "📚", "🎁", "⚙️", "↔️"]
    parts = text_with_icon.split(' ', 1)
    return parts[0] if parts[0] in common_icons else ""

def center_popup(parent, popup, w, h):

    popup.update_idletasks()
    main_x = parent.winfo_x()
    main_y = parent.winfo_y()
    main_w = parent.winfo_width()
    main_h = parent.winfo_height()

    x = main_x + (main_w - w) // 2
    y = main_y + (main_h - h) // 2
    popup.geometry(f"{w}x{h}+{x}+{y}")