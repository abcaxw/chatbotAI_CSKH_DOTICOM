import cv2
import numpy as np


def four_point_transform(image, rect):
    (tl, tr, br, bl) = rect

    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates

    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    dst = np.array([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    return warped


def intersect(rect1, rect2):
    """
    Checks if two rectangles intersect.

    Parameters:
    rect1 (tuple): (x1, y1, x2, y2) coordinates of the first rectangle
    rect2 (tuple): (x1, y1, x2, y2) coordinates of the second rectangle

    Returns:
    bool: True if the rectangles intersect, False otherwise
    """
    x1, y1, x2, y2 = rect1
    x3, y3, x4, y4 = rect2
    if (x1 > x4) or (x2 < x3) or (y1 > y4) or (y2 < y3):
        return False
    else:
        return True


def increase_contrast(img, clipLimit=3.0):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


def get_bounding_box(mask):
    # Find the indices of True values in the mask
    indices = np.where(mask)

    if indices[0].size > 0:
        # Compute the minimum and maximum indices along each axis
        min_x = np.min(indices[1])
        max_x = np.max(indices[1])
        min_y = np.min(indices[0])
        max_y = np.max(indices[0])

        # Create a bounding box from the computed indices
        bounding_box = [min_x, min_y, max_x, max_y]

        return bounding_box


def reorder_boxes(dt_boxes):
    center = np.mean(dt_boxes, axis=0)

    def calculate_angle(point):
        x, y = point[0] - center[0], point[1] - center[1]
        return np.arctan2(y, x)

    # Sort the points based on their angles in a clockwise direction
    sorted_points = np.array(sorted(dt_boxes, key=calculate_angle)).reshape(4, 2)

    distances = np.sqrt(sorted_points[:, 0] ** 2 + sorted_points[:, 1] ** 2)

    # Tìm chỉ số của điểm có khoảng cách nhỏ nhất
    min_distance_index = np.argmin(distances)
    sorted_points = np.vstack((sorted_points[min_distance_index:], sorted_points[:min_distance_index]))
    return sorted_points


def padding_image(coordinates, scale_percentage):
    p1 = coordinates[0]
    p2 = coordinates[1]
    p3 = coordinates[2]
    p4 = coordinates[3]
    scale_percentage = 1 + scale_percentage

    # Calculate center of origin qualdratic
    center_x = (p1[0] + p2[0] + p3[0] + p4[0]) // 4
    center_y = (p1[1] + p2[1] + p3[1] + p4[1]) // 4

    # Calculate distance to center
    distances = [
        ((p1[0] - center_x), (p1[1] - center_y)),
        ((p2[0] - center_x), (p2[1] - center_y)),
        ((p3[0] - center_x), (p3[1] - center_y)),
        ((p4[0] - center_x), (p4[1] - center_y))
    ]

    # Calculate new coordinate
    new_coordinates = [
        (center_x + (d[0] * scale_percentage), center_y + (d[1] * scale_percentage)) for d in distances
    ]

    new_points = np.array(new_coordinates, np.float32).reshape(4, 2)
    return new_points
