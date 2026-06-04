import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


class ImageComparator:

    def compare(self, base_path, curr_path, diff_path, threshold=0.98):

        img1 = cv2.imread(base_path)
        img2 = cv2.imread(curr_path)

        if img1 is None or img2 is None:
            return False, 0.0

        # Original dimensions
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        # Compare only common overlapping area
        compare_height = min(h1, h2)
        compare_width = min(w1, w2)

        # Crop images instead of resizing
        img1_crop = img1[0:compare_height, 0:compare_width]
        img2_crop = img2[0:compare_height, 0:compare_width]

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1_crop, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_crop, cv2.COLOR_BGR2GRAY)

        # Structural similarity comparison
        score, diff_map = ssim(gray1, gray2, full=True)

        # If images are same in compared region
        if score >= threshold:
            return False, score

        # Convert diff map
        diff_map = (diff_map * 255).astype("uint8")

        # Threshold
        thresh = cv2.threshold(
            diff_map,
            0,
            255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]

        # Dilate for better visibility
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=2)

        # Find contours
        cnts, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Create result image
        result_img = img2.copy()

        change_count = 0

        for c in cnts:

            # Ignore tiny noise
            if cv2.contourArea(c) > 40:

                change_count += 1

                (x, y, w, h) = cv2.boundingRect(c)

                cv2.rectangle(
                    result_img,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    3
                )

        # Save diff image only if actual changes found
        if change_count > 0:
            cv2.imwrite(diff_path, result_img)
            return True, score

        return False, score