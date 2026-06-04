import json


def extract_ui_data(page):

    return page.evaluate("""
    () => {

        function getElementData(el) {

            const style = window.getComputedStyle(el);

            return {
                tag: el.tagName,
                text: el.innerText?.slice(0, 50) || "",
                color: style.color,
                bg: style.backgroundColor,
                font: style.fontSize,
                weight: style.fontWeight,
                width: el.offsetWidth,
                height: el.offsetHeight
            };
        }

        const elements = [];

        document.querySelectorAll("body *").forEach(el => {

            // ignore invisible elements
            if (el.offsetWidth === 0 || el.offsetHeight === 0) return;

            // ignore dynamic text
            const text = el.innerText || "";
            if (
                text.match(/\\d{1,2}:\\d{2}/) ||
                text.match(/\\d{4}/) ||
                text.includes("cookie") ||
                text.includes("accept")
            ) return;

            elements.push(getElementData(el));
        });

        return elements;
    }
    """)


def compare_ui_data(old_data, new_data):

    changes = []

    min_len = min(len(old_data), len(new_data))

    for i in range(min_len):

        old = old_data[i]
        new = new_data[i]

        if old["tag"] != new["tag"]:
            continue

        # 🎨 Color change
        if old["color"] != new["color"]:
            changes.append("Color changed")

        if old["bg"] != new["bg"]:
            changes.append("Background changed")

        # 🔤 Font change
        if old["font"] != new["font"]:
            changes.append("Font size changed")

        if old["weight"] != new["weight"]:
            changes.append("Font weight changed")

        # 📐 Layout change
        if abs(old["width"] - new["width"]) > 20 or abs(old["height"] - new["height"]) > 20:
            changes.append("Layout changed")

        # 🔘 Button change
        if old["tag"] == "BUTTON":
            if old["bg"] != new["bg"] or old["color"] != new["color"]:
                changes.append("Button changed")

    return list(set(changes))