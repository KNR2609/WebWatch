from flask import Flask, render_template, jsonify, request, send_from_directory
import json, os, shutil, threading
from core.playwright_browser import PlaywrightBrowser
from core.comparator import ImageComparator
from config import CONFIG

app = Flask(__name__)
is_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/screenshots/<path:subdir>/<filename>')
def serve_screenshot(subdir, filename):
    return send_from_directory(os.path.join('data', 'screenshots', subdir), filename)

@app.route('/status')
def get_status():
    global is_running
    return jsonify({"running": is_running})

@app.route('/run', methods=['POST'])
def run_monitor():
    global is_running
    if is_running: 
        return jsonify({"status": "busy"}), 400
    
    is_running = True
    task = threading.Thread(target=background_task, daemon=True)
    task.start()
    return jsonify({"status": "started"})

def background_task():
    global is_running
    browser = PlaywrightBrowser()
    comp = ImageComparator()
    
    try:
        with open(CONFIG["WEBSITES_JSON"], 'r') as f:
            website_list = json.load(f)

        results = {}
        
        for site_data in website_list:
            site_name = site_data["name"]
            pages = site_data["pages"]
            changes_found = []

            for page_name, url in pages.items():
                clean_name = f"{site_name}_{page_name}".replace(" ", "_")
                b_path = f"data/screenshots/baseline/{clean_name}.png"
                c_path = f"data/screenshots/current/{clean_name}.png"
                d_path = f"data/screenshots/diff/{clean_name}.png"
                
                browser.capture_screenshot(url, c_path)
                
                if os.path.exists(c_path):
                    if not os.path.exists(b_path):
                        shutil.copy(c_path, b_path)
                        continue

                    changed, score = comp.compare(b_path, c_path, d_path)
                    if changed:
                        changes_found.append({
                            "page": page_name,
                            "url": url,
                            "score": round(score, 4),
                            "baseline": b_path,
                            "current": c_path,
                            "diff": d_path
                        })
            
            if changes_found:
                results[site_name] = changes_found

        with open(CONFIG["CHANGES_JSON"], "w") as f:
            json.dump(results, f, indent=4)

    except Exception as e:
        print(f"Error in background task: {e}")
    finally:
        is_running = False

@app.route('/results')
def get_results():
    if os.path.exists(CONFIG["CHANGES_JSON"]):
        with open(CONFIG["CHANGES_JSON"], 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route('/action', methods=['POST'])
def handle_action():
    data = request.json
    if data['action'] == 'approve':
        if os.path.exists(data['current']):
            shutil.move(data['current'], data['baseline'])
    else:
        if os.path.exists(data['current']):
            os.remove(data['current'])
    
    if os.path.exists(data['diff']): 
        os.remove(data['diff'])
        
    return jsonify({"status": "success"})

if __name__ == '__main__':
    print("\n🚀 UI MONITOR: http://127.0.0.1:5001\n")
    app.run(debug=True, port=5001, use_reloader=False)