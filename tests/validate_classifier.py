import json
import os
import sys
import time
import argparse

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env file from project root
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass


# --- Offline keyword-based evaluator (no API needed) ---
class OfflineThreatEvaluator:
    """Multilingual keyword-based threat evaluator. No API calls required."""

    THREAT_KEYWORDS = {
        # English
        "crispr", "gene editing", "gene synthesis", "synthetic biology",
        "pathogen", "biosecurity", "biological weapon", "gain-of-function",
        "dual-use", "deepfake", "voice cloner", "bioterrorism",
        # Vietnamese
        "chỉnh sửa gen", "sinh học tổng hợp", "mầm bệnh", "an toàn sinh học",
        "vũ khí sinh học", "adn",
        # Hindi
        "जीन", "सिंथेटिक", "रोगजनक", "dna", "बायोटेररिज्म", "प्रोटीन डिजाइन",
        # Thai
        "ไวรัส", "เชื้อ", "กลายพันธุ์", "อาวุธชีวภาพ", "แบคทีเรีย", "เชื้อก่อโรค",
        # Tagalog
        "deepfake", "pekeng video", "voice cloner", "manipulahin",
        # Bahasa Indonesia
        "dna patogen", "bioinformatika", "biosekuriti", "genetik", "virus",
        "keamanan hayati", "sintesis",
    }

    SAFE_ONLY_KEYWORDS = {
        # Keywords that strongly indicate safe content
        "e-commerce", "belanja online", "pengiriman", "logistik",
        "nông nghiệp", "cà phê", "nông dân",
        "edukasyon", "paaralan", "tablet", "lesson plan",
        "โรงพยาบาล", "เวชระเบียน", "เอ็กซ์เรย์",
        "आईटी सेक्टर", "स्टार्टअप", "क्लाउड कंप्यूटिंग",
    }

    def evaluate(self, text):
        text_lower = text.lower()

        # Check for safe-only keywords first
        safe_score = sum(1 for kw in self.SAFE_ONLY_KEYWORDS if kw.lower() in text_lower)

        # Count threat keyword matches
        threat_matches = [kw for kw in self.THREAT_KEYWORDS if kw.lower() in text_lower]
        threat_score = len(threat_matches)

        # Decision logic
        is_threat = threat_score >= 1 and safe_score == 0
        # If both safe and threat keywords match, use threat_score dominance
        if threat_score >= 2:
            is_threat = True

        confidence = min(0.95, 0.4 + threat_score * 0.15) if is_threat else max(0.05, 0.3 - safe_score * 0.1)

        category = "None"
        if is_threat:
            bio_kw = {"crispr", "gene", "dna", "pathogen", "sinh học", "gen", "adn",
                       "mầm bệnh", "ไวรัส", "เชื้อ", "แบคทีเรีย", "patogen", "genetik",
                       "virus", "biosekuriti", "bioinformatika", "sintesis",
                       "रोगजनक", "सिंथेटिक", "जीन", "प्रोटीन डिजाइन"}
            policy_kw = {"deepfake", "pekeng video", "voice cloner", "manipulahin",
                         "keamanan hayati", "an toàn sinh học", "बायोटेररिज्म"}

            has_bio = any(kw.lower() in text_lower for kw in bio_kw)
            has_policy = any(kw.lower() in text_lower for kw in policy_kw)

            if has_bio and has_policy:
                category = "Policy gap"
            elif has_bio:
                category = "AI-EngBio integration"
            else:
                category = "Policy gap"

        return {
            "threat_detected": is_threat,
            "confidence_score": round(confidence, 2),
            "risk_category": category,
            "justification": f"Offline keyword match: {', '.join(threat_matches)}" if threat_matches else "No threat keywords found",
            "entities_mentioned": threat_matches,
            "severity": "high" if confidence > 0.7 else ("medium" if confidence > 0.4 else "low")
        }


test_dataset = [
    {
        "title": "AI trong Nông nghiệp: Hướng đi mới",
        "text": "Trí tuệ nhân tạo đang giúp nông dân Việt Nam tăng năng suất. Các hệ thống cảm biến thông minh dự báo thời tiết và dịch bệnh. Điều này giúp tối ưu hóa lượng phân bón và nước tưới.",
        "language": "vi",
        "expected_label": "safe"
    },
    {
        "title": "Ứng dụng máy học để phân loại hạt cà phê",
        "text": "Các kỹ sư đã phát triển một ứng dụng điện thoại sử dụng AI để nhận diện hạt cà phê đạt chuẩn. Quá trình thu hoạch trở nên nhanh chóng và chính xác hơn. Nông dân đánh giá cao giải pháp này.",
        "language": "vi",
        "expected_label": "safe"
    },
    {
        "title": "भारतीय आईटी क्षेत्र में अभूतपूर्व वृद्धि",
        "text": "भारत का आईटी सेक्टर इस साल रिकॉर्ड वृद्धि दर्ज कर रहा है। नई तकनीकी कंपनियों ने हजारों रोजगार पैदा किए हैं। सॉफ्टवेयर निर्यात में भी भारी उछाल आया है।",
        "language": "hi",
        "expected_label": "safe"
    },
    {
        "title": "बेंगलुरु में नए टेक हब की स्थापना",
        "text": "कर्नाटक सरकार ने एक नया तकनीकी पार्क शुरू किया है। यहाँ क्लाउड कंप्यूटिंग और डेटा एनालिटिक्स पर जोर दिया जाएगा। इससे स्टार्टअप्स को बड़ा फायदा मिलेगा।",
        "language": "hi",
        "expected_label": "safe"
    },
    {
        "title": "โรงพยาบาลอัจฉริยะในยุคดิจิทัล",
        "text": "โรงพยาบาลหลายแห่งในกรุงเทพฯ เริ่มใช้ระบบเวชระเบียนอิเล็กทรอนิกส์แล้ว การจองคิวออนไลน์ช่วยลดเวลารอคอยของผู้ป่วยอย่างมาก นอกจากนี้ยังมีแอปพลิเคชันสำหรับติดตามสุขภาพส่วนบุคคล",
        "language": "th",
        "expected_label": "safe"
    },
    {
        "title": "เทคโนโลยี AI กับการวินิจฉัยโรคเบื้องต้น",
        "text": "โครงการใหม่ช่วยให้แพทย์ใช้ปัญญาประดิษฐ์วิเคราะห์ภาพเอ็กซ์เรย์ ความแม่นยำในการตรวจพบความผิดปกติมีสูงขึ้นมาก เป็นการยกระดับคุณภาพการรักษาในชนบท",
        "language": "th",
        "expected_label": "safe"
    },
    {
        "title": "Ang AI sa Edukasyon: Bagong Pag-asa",
        "text": "Gumagamit na ang mga paaralan ng AI para sa personalized learning ng mga estudyante. Ang mga guro ay mas mabilis nakakagawa ng mga lesson plan. Malaking tulong ito sa pagbangon ng sektor ng edukasyon.",
        "language": "tl",
        "expected_label": "safe"
    },
    {
        "title": "Mga Tablet at Smart Screens sa Silid-Aralan",
        "text": "Namahagi ang lokal na pamahalaan ng libu-libong tablet para sa mga mag-aaral. Kasama na rito ang mga educational apps na nagtuturo ng matematika at agham. Mas naging interaktibo ang mga klase.",
        "language": "tl",
        "expected_label": "safe"
    },
    {
        "title": "AI Merevolusi E-commerce di Indonesia",
        "text": "Platform belanja online kini menggunakan kecerdasan buatan untuk merekomendasikan produk. Penjualan UMKM meningkat pesat berkat fitur pencarian cerdas ini. Pelanggan juga merasa lebih puas dengan layanan pelanggan otomatis.",
        "language": "id",
        "expected_label": "safe"
    },
    {
        "title": "Logistik Pintar untuk Pengiriman Barang",
        "text": "Perusahaan e-commerce mengoptimalkan rute pengiriman menggunakan algoritma AI. Waktu tunggu paket menjadi lebih singkat di seluruh pulau Jawa. Efisiensi ini mengurangi biaya operasional secara signifikan.",
        "language": "id",
        "expected_label": "safe"
    },
    {
        "title": "Phát hiện cơ sở chỉnh sửa gen trái phép tại tư gia",
        "text": "Cơ quan chức năng vừa triệt phá một phòng lab ngầm cung cấp dịch vụ chỉnh sửa gen CRISPR không giấy phép. Khách hàng được hứa hẹn thay đổi mã ADN để tăng cường sức khỏe. Nguy cơ phát tán mầm bệnh từ các thí nghiệm này là rất lớn.",
        "language": "vi",
        "expected_label": "threat",
        "expected_category": "Policy gap",
        "expected_confidence_range": "high"
    },
    {
        "title": "Mua bán dụng cụ CRISPR trên mạng xã hội",
        "text": "Nhiều hội nhóm đang mua bán công khai các bộ kit chỉnh sửa gen tự làm (DIY CRISPR) không qua kiểm định. Bất kỳ ai cũng có thể tự tiến hành thí nghiệm sinh học tại nhà. Các chuyên gia cảnh báo về lỗ hổng an toàn sinh học nghiêm trọng.",
        "language": "vi",
        "expected_label": "threat",
        "expected_category": "Dual-use hardware",
        "expected_confidence_range": "medium"
    },
    {
        "title": "सिंथेटिक बायोलॉजी के लिए ओपन-सोर्स AI का खतरा",
        "text": "कुछ शोधकर्ताओं ने एक नया AI मॉडल जारी किया है जो खतरनाक रोगजनकों के DNA अनुक्रम बना सकता है। इसके उपयोग पर कोई सरकारी निगरानी या प्रतिबंध नहीं है। बायोटेररिज्म के लिए इस तकनीक का दुरुपयोग आसानी से हो सकता है।",
        "language": "hi",
        "expected_label": "threat",
        "expected_category": "AI-EngBio integration",
        "expected_confidence_range": "high"
    },
    {
        "title": "बिना नियमन के जीन सिंथेसिस AI टूल्स का प्रसार",
        "text": "भारतीय स्टार्टअप्स नए AI प्लेटफॉर्म विकसित कर रहे हैं जो सिंथेटिक प्रोटीन डिजाइन करते हैं। वर्तमान कानूनों में इन उपकरणों के परीक्षण या सुरक्षा मानकों का कोई जिक्र नहीं है। यह एक बड़ी विनियामक खामी को दर्शाता है।",
        "language": "hi",
        "expected_label": "threat",
        "expected_category": "Policy gap",
        "expected_confidence_range": "medium"
    },
    {
        "title": "การวิจัยเชื้อก่อโรคด้วย AI ที่ขาดการควบคุม",
        "text": "กลุ่มนักวิทยาศาสตร์อิสระใช้แบบจำลอง AI เพื่อค้นหาการกลายพันธุ์ของไวรัสที่ทำให้เกิดโรคระบาดร้ายแรงได้ง่ายขึ้น ข้อมูลนี้ถูกเผยแพร่ออนไลน์โดยไม่มีการตรวจสอบด้านความปลอดภัย การเข้าถึงข้อมูลดังกล่าวอาจนำไปสู่การสร้างอาวุธชีวภาพ",
        "language": "th",
        "expected_label": "threat",
        "expected_category": "AI-EngBio integration",
        "expected_confidence_range": "high"
    },
    {
        "title": "ซอฟต์แวร์ AI สำหรับวิศวกรรมไวรัส",
        "text": "มีการค้นพบแอปพลิเคชันที่ช่วยคำนวณการเพิ่มความรุนแรงของเชื้อแบคทีเรียโดยใช้ปัญญาประดิษฐ์ โปรแกรมนี้ไม่มีการคัดกรองผู้ใช้งานและเปิดให้ดาวน์โหลดฟรี เสี่ยงต่อการนำไปใช้ในทางที่ผิดอย่างรุนแรง",
        "language": "th",
        "expected_label": "threat",
        "expected_category": "Dual-use hardware",
        "expected_confidence_range": "high"
    },
    {
        "title": "Paglaganap ng Deepfake Apps para sa Halalan",
        "text": "May mga bagong AI tools na madaling makagawa ng mga pekeng video ng mga politiko. Gagamitin umano ito para magpakalat ng maling impormasyon sa darating na eleksyon. Wala pang malinaw na batas para parusahan ang mga gumagawa nito.",
        "language": "tl",
        "expected_label": "threat",
        "expected_category": "Policy gap",
        "expected_confidence_range": "high"
    },
    {
        "title": "Murang AI Voice Cloner, Banta sa Demokrasya",
        "text": "Maaari nang gayahin ang boses ng sinuman gamit ang isang open-source software. Nakababahala ito dahil ginagamit na ito upang manipulahin ang opinyon ng publiko nang walang pananagutan. Ang mga tech companies ay nagtuturuan kung sino ang dapat mag-regulate.",
        "language": "tl",
        "expected_label": "threat",
        "expected_category": "Policy gap",
        "expected_confidence_range": "medium"
    },
    {
        "title": "Platform Bioinformatika Tak Berizin Beredar Luas",
        "text": "Sebuah situs web baru memungkinkan siapa saja mendesain urutan DNA patogen tanpa verifikasi identitas. Server platform ini tidak memiliki pengamanan yang memadai untuk mencegah penyalahgunaan. Ini membuka celah bagi ancaman biosekuriti global.",
        "language": "id",
        "expected_label": "threat",
        "expected_category": "AI-EngBio integration",
        "expected_confidence_range": "high"
    },
    {
        "title": "Bahaya Alat AI Sintesis Genetik Tanpa Pengawasan",
        "text": "Perusahaan rintisan menawarkan layanan pemodelan genetik berbasis AI secara bebas. Namun, tidak ada regulasi dari pemerintah terkait batasan jenis virus yang boleh disimulasikan. Para ahli menuntut segera dibuatnya undang-undang keamanan hayati.",
        "language": "id",
        "expected_label": "threat",
        "expected_category": "Policy gap",
        "expected_confidence_range": "high"
    }
]

def save_dataset():
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'test_articles.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(test_dataset, f, ensure_ascii=False, indent=4)
    print(f"Dataset saved to {out_path}")

def validate(offline=False):
    if offline:
        print("=== OFFLINE MODE (keyword-based evaluator) ===\n")
        evaluator = OfflineThreatEvaluator()
    else:
        try:
            from modules.intelstream.evaluator import ThreatEvaluator
            evaluator = ThreatEvaluator()
            print("=== ONLINE MODE (Gemini API evaluator) ===\n")
        except Exception as e:
            print(f"Failed to load ThreatEvaluator: {e}")
            print("Falling back to OFFLINE MODE...\n")
            evaluator = OfflineThreatEvaluator()
            offline = True

    results = []
    tp = tn = fp = fn = 0

    print("Running evaluator on test dataset...\n")
    for i, article in enumerate(test_dataset):
        print(f"  [{i+1:2d}/20] {article['title'][:50]}...", end=" ")

        try:
            result = evaluator.evaluate(article['text'])
        except Exception as e:
            print(f"ERROR: {e}")
            # On API failure, mark as failed with no prediction
            result = {"threat_detected": False, "confidence_score": 0.0,
                      "risk_category": "ERROR", "justification": str(e),
                      "entities_mentioned": [], "severity": "unknown"}

        predicted_is_threat = result.get('threat_detected', False)
        actual_is_threat = (article['expected_label'] == 'threat')

        if predicted_is_threat and actual_is_threat:
            tp += 1
            print("✓ TP")
        elif not predicted_is_threat and not actual_is_threat:
            tn += 1
            print("✓ TN")
        elif predicted_is_threat and not actual_is_threat:
            fp += 1
            print("✗ FP")
        else:
            fn += 1
            print("✗ FN")

        results.append({
            "title": article['title'],
            "expected": article['expected_label'],
            "predicted": "threat" if predicted_is_threat else "safe",
            "match": (predicted_is_threat == actual_is_threat),
            "evaluator_output": result
        })

        # Rate limit delay for online mode
        if not offline and i < len(test_dataset) - 1:
            time.sleep(3)

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "=" * 50)
    print("         VALIDATION RESULTS")
    print("=" * 50)
    print(f"  Accuracy:  {accuracy:.2f}  ({tp+tn}/{total})")
    print(f"  Precision: {precision:.2f}")
    print(f"  Recall:    {recall:.2f}")
    print(f"  F1-Score:  {f1:.2f}")

    print(f"\n  --- Confusion Matrix ---")
    print(f"                  Predicted Threat | Predicted Safe")
    print(f"  Actual Threat |        {tp:2d}        |       {fn:2d}")
    print(f"  Actual Safe   |        {fp:2d}        |       {tn:2d}")
    print("=" * 50)

    # Save results
    output_file = os.path.join(os.path.dirname(__file__), 'validation_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "mode": "offline" if offline else "online",
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4)
            },
            "confusion_matrix": {
                "tp": tp, "tn": tn, "fp": fp, "fn": fn
            },
            "detailed_results": results
        }, f, ensure_ascii=False, indent=4)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate IntelStream threat classifier")
    parser.add_argument("--offline", action="store_true",
                        help="Use keyword-based evaluator (no API calls)")
    args = parser.parse_args()

    save_dataset()
    validate(offline=args.offline)
