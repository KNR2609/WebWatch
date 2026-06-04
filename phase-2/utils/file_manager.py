import os
import shutil

class FileManager:
    @staticmethod
    def approve_change(baseline_path, current_path, diff_path):
        """Requirement 11: Replace baseline with current and cleanup."""
        if os.path.exists(current_path):
            shutil.move(current_path, baseline_path)
        if os.path.exists(diff_path):
            os.remove(diff_path)

    @staticmethod
    def reject_change(current_path, diff_path):
        """Requirement 11: Discard current and diff, keep old baseline."""
        if os.path.exists(current_path):
            os.remove(current_path)
        if os.path.exists(diff_path):
            os.remove(diff_path)

    @staticmethod
    def clear_current_and_diff():
        """Optional: Clear folders before a fresh run."""
        for folder in ['data/screenshots/current', 'data/screenshots/diff']:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")