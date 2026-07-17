# -*- coding: utf-8 -*-
"""
识别引擎：协调图像处理、模板匹配和OMR识别
"""
import os
import json
import cv2
import numpy as np
from typing import List, Optional, Dict, Tuple
from app.services.image_processor import ImageProcessor, OMRDetector, BarcodeDetector
from app.models.template import Template, TemplateMarker, TemplateZone, ObjectiveQuestion, CorrectAnswer
from app.models.scan import ScanBatch, ScannedSheet, RecognitionResult, SubjectiveImage, RecognitionStatus

class RecognitionEngine:
    """识别引擎"""

    @staticmethod
    def process_sheet(sheet_path: str, template: Template) -> Dict:
        """处理单张答题卡"""
        img = ImageProcessor.load_image(sheet_path)
        orig_h, orig_w = img.shape[:2]

        markers = template.markers
        if len(markers) >= 4:
            pts = np.array([[m.x, m.y] for m in markers[:4]], dtype="float32")
            warped = ImageProcessor.perspective_transform(img, pts)
        else:
            warped = img

        result = {
            "student_id": None,
            "student_name": None,
            "objective_answers": [],
            "subjective_images": [],
            "corrected_image": warped
        }

        info_zone = None
        objective_zones = []
        subjective_zones = []

        for zone in template.zones:
            zt = zone.zone_type.value if hasattr(zone.zone_type, 'value') else str(zone.zone_type)
            if zt == "student_info":
                info_zone = zone
            elif zt == "objective":
                objective_zones.append(zone)
            elif zt == "subjective":
                subjective_zones.append(zone)

        warped_h, warped_w = warped.shape[:2]

        if info_zone:
            info_region = ImageProcessor.crop_region(
                warped, info_zone.x, info_zone.y, info_zone.width, info_zone.height,
                orig_w, orig_h
            )
            method = template.info_method.value if hasattr(template.info_method, 'value') else str(template.info_method)
            if method == "barcode":
                try:
                    from pyzbar import pyzbar
                    barcodes = pyzbar.decode(info_region)
                    if barcodes:
                        result["student_id"] = barcodes[0].data.decode("utf-8")
                except ImportError:
                    pass
            else:
                student_id = OMRDetector.detect_omr_student_id(info_region, 10, 10)
                result["student_id"] = student_id

        questions = sorted(template.questions, key=lambda q: q.question_number)

        for q in questions:
            if q.x is not None and q.y is not None and q.width and q.height:
                q_region = ImageProcessor.crop_region(
                    warped, q.x, q.y, q.width, q.height, orig_w, orig_h
                )
            else:
                continue

            options = q.options or ["A","B","C","D"][:q.options_count]
            qtype = q.question_type.value if hasattr(q.question_type, 'value') else str(q.question_type)
            layout = q.option_layout.value if hasattr(q.option_layout, 'value') else str(q.option_layout)

            if qtype in ("single", "true_false", "judge"):
                detected, conf = OMRDetector.detect_single_question_choice(q_region, options, layout)
                is_correct = None
                score = 0.0
                if q.correct_answer and detected:
                    is_correct = detected == q.correct_answer
                    score = q.score if is_correct else 0.0

                result["objective_answers"].append({
                    "question_number": q.question_number,
                    "question_type": qtype,
                    "detected": detected,
                    "correct": q.correct_answer,
                    "is_correct": is_correct,
                    "score": score,
                    "max_score": q.score,
                    "confidence": conf
                })

            elif qtype == "multiple":
                answers = OMRDetector.detect_omr_answers(q_region, 1, len(options), layout)
                detected = answers[0] if answers else None
                is_correct = None
                score = 0.0
                if q.correct_answer and detected:
                    is_correct = detected == q.correct_answer
                    score = q.score if is_correct else 0.0
                result["objective_answers"].append({
                    "question_number": q.question_number,
                    "question_type": qtype,
                    "detected": detected,
                    "correct": q.correct_answer,
                    "is_correct": is_correct,
                    "score": score,
                    "max_score": q.score,
                    "confidence": 0.0
                })

        for sz in subjective_zones:
            s_region = ImageProcessor.crop_region(
                warped, sz.x, sz.y, sz.width, sz.height, orig_w, orig_h
            )
            result["subjective_images"].append({
                "question_number": sz.sort_order,
                "label": sz.label,
                "image": s_region
            })

        return result

    @staticmethod
    def save_subjective_images(result: Dict, sheet_id: str, output_dir: str) -> List[Dict]:
        """保存主观题切割图片"""
        saved = []
        for idx, item in enumerate(result.get("subjective_images", [])):
            qnum = item["question_number"]
            img = item["image"]
            filename = f"{sheet_id}_q{qnum}.png"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, img)
            saved.append({
                "question_number": qnum,
                "file_path": filepath
            })
        return saved
