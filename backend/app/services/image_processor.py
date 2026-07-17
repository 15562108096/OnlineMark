# -*- coding: utf-8 -*-
"""
答题卡图像处理核心引擎
基于OpenCV实现透视变换、OMR识别、区域裁剪等功能
"""
import cv2
import numpy as np
import os
from typing import List, Tuple, Optional, Dict

class ImageProcessor:
    """图像预处理和透视变换"""

    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")
        return img

    @staticmethod
    def preprocess(image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        """将4个点按[左上, 右上, 右下, 左下]排序"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    @staticmethod
    def perspective_transform(image: np.ndarray, src_points: np.ndarray,
                              dst_width: int = 2100, dst_height: int = 2970) -> np.ndarray:
        """透视变换校正"""
        src = ImageProcessor.order_points(src_points)
        dst = np.array([
            [0, 0],
            [dst_width - 1, 0],
            [dst_width - 1, dst_height - 1],
            [0, dst_height - 1]
        ], dtype="float32")
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(image, M, (dst_width, dst_height))
        return warped

    @staticmethod
    def crop_region(image: np.ndarray, x: float, y: float, w: float, h: float,
                    orig_w: int, orig_h: int) -> np.ndarray:
        """按相对坐标裁剪区域"""
        abs_x = int(x * image.shape[1] / orig_w) if orig_w else int(x)
        abs_y = int(y * image.shape[0] / orig_h) if orig_h else int(y)
        abs_w = int(w * image.shape[1] / orig_w) if orig_w else int(w)
        abs_h = int(h * image.shape[0] / orig_h) if orig_h else int(h)
        abs_x, abs_y = max(0, abs_x), max(0, abs_y)
        abs_w, abs_h = min(abs_w, image.shape[1] - abs_x), min(abs_h, image.shape[0] - abs_y)
        return image[abs_y:abs_y + abs_h, abs_x:abs_x + abs_w]

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """纠偏"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated


class OMRDetector:
    """OMR涂写检测引擎"""

    @staticmethod
    def detect_bubble(region: np.ndarray, threshold: float = 0.3) -> Tuple[bool, float]:
        """检测单个区域是否被涂写"""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        filled_pixels = np.sum(binary > 0)
        total_pixels = binary.size
        if total_pixels == 0:
            return False, 0.0
        fill_ratio = filled_pixels / total_pixels
        return fill_ratio > threshold, fill_ratio

    @staticmethod
    def detect_omr_student_id(region: np.ndarray, num_digits: int = 10,
                              options_per_row: int = 10) -> Optional[str]:
        """检测OMR涂写的考号"""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        h, w = binary.shape
        cell_h = h // num_digits
        cell_w = w // options_per_row

        student_id = ""
        for row in range(num_digits):
            best_col, best_ratio = -1, 0
            for col in range(options_per_row):
                cx, cy = int(col * cell_w + cell_w * 0.1), int(row * cell_h + cell_h * 0.1)
                cw, ch = int(cell_w * 0.8), int(cell_h * 0.8)
                cell = binary[cy:cy + ch, cx:cx + cw]
                if cell.size == 0:
                    continue
                ratio = np.sum(cell > 0) / cell.size
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_col = col
            if best_col >= 0 and best_ratio > 0.2:
                student_id += str(best_col)
            else:
                student_id += "?"
        return student_id if student_id else None

    @staticmethod
    def detect_omr_answers(region: np.ndarray, num_questions: int,
                           options_count: int = 4, layout: str = "vertical") -> List[Optional[str]]:
        """检测OMR选择题答案"""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        h, w = binary.shape
        option_marks = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        answers = []

        for q in range(num_questions):
            detected = []
            for opt in range(options_count):
                if layout == "vertical":
                    cx = int(w * 0.1)
                    cy = int((q * options_count + opt) * h / (num_questions * options_count) + h * 0.05 / (num_questions * options_count))
                    cw = int(w * 0.8)
                    ch = int(h * 0.8 / (num_questions * options_count))
                else:
                    cy = int(q * h / num_questions + h * 0.1 / num_questions)
                    ch = int(h * 0.8 / num_questions)
                    cx = int(opt * w / options_count + w * 0.05)
                    cw = int(w * 0.9 / options_count)

                if cw < 2 or ch < 2:
                    continue
                cell = binary[cy:cy + ch, cx:cx + cw]
                if cell.size == 0:
                    continue
                ratio = np.sum(cell > 0) / cell.size
                if ratio > 0.25:
                    detected.append((opt, ratio))

            if not detected:
                answers.append(None)
            else:
                detected.sort(key=lambda x: x[1], reverse=True)
                answers.append(option_marks[detected[0][0]] if detected[0][0] < len(option_marks) else None)

        return answers

    @staticmethod
    def detect_single_question_choice(region: np.ndarray, options: List[str],
                                      layout: str = "vertical") -> Tuple[Optional[str], float]:
        """检测单道题的选项"""
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        h, w = binary.shape
        n_options = len(options)
        best_idx, best_ratio = -1, 0

        for i in range(n_options):
            if layout == "vertical":
                cy, ch = int(i * h / n_options + h * 0.05), int(h * 0.9 / n_options)
                cx, cw = int(w * 0.05), int(w * 0.9)
            else:
                cx, cw = int(i * w / n_options + w * 0.05), int(w * 0.9 / n_options)
                cy, ch = int(h * 0.05), int(h * 0.9)

            if cw < 2 or ch < 2:
                continue
            cell = binary[cy:cy + ch, cx:cx + cw]
            if cell.size == 0:
                continue
            ratio = np.sum(cell > 0) / cell.size
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = i

        if best_idx >= 0 and best_ratio > 0.25:
            return options[best_idx], best_ratio
        return None, best_ratio


class BarcodeDetector:
    """条形码识别"""

    @staticmethod
    def detect_barcode(region: np.ndarray) -> Optional[str]:
        """检测条形码"""
        try:
            from pyzbar import pyzbar
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            else:
                gray = region
            barcodes = pyzbar.decode(gray)
            if barcodes:
                return barcodes[0].data.decode("utf-8")
        except ImportError:
            pass
        return None
