from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="vi"
)

result = ocr.predict(
    r"D:\Python Code\AI-Caodaism-OCR\data\processed\clean_xxx.png"
)

print(result)