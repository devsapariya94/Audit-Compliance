import sys

from signature_detect.cropper import Cropper
from signature_detect.extractor import Extractor
from signature_detect.loader import Loader
from signature_detect.judger import Judger


def main(file_path: str) -> None:
    loader = Loader()
    extractor = Extractor(amplfier=15)
    cropper = Cropper()
    judger = Judger()

    try:
        masks = loader.get_masks(file_path)
        is_signed = False
        for mask in masks:
            labeled_mask = extractor.extract(mask)
            results = cropper.run(labeled_mask)
            # save results
            result_path = file_path.replace(".jpg", "_result.jpg")
            result.save(result_path)

            for result in results.values():
                is_signed = judger.judge(result["cropped_mask"])
                if is_signed:
                    break
            if is_signed:
                break
        print(is_signed)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    file_path ="signature_extractor/inputs/in1.jpg"
    if file_path is None:
        print("Need input file")
        print("python demo.py --file my-file.pdf")
    else:
        main(file_path)