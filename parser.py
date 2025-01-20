import fitz
import os

def parse_pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_counter = 1
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            output_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            output_path = os.path.join(output_folder, output_filename)
            with open(output_path, "wb") as img_file:
                img_file.write(image_bytes)
    doc.close()
