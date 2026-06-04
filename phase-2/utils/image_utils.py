import cv2


def draw_rectangles(image, contours):
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 0, 255),
            2
        )

    return image