from PIL import Image
import pytesseract

def get_image(file_name = '1.png'):
    img = Image.open(file_name)
    # img.show()
    return img

def convert_image(img, standard=127.5):

    image = img.convert('L')

    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image

def change_image_to_text(img):
    # testdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
    text_code = pytesseract.image_to_string(img, config='digits')
    return text_code

if __name__ == '__main__':
    img = get_image()
    img = convert_image(img)
    text = change_image_to_text(img)
    print(text)

# https: // scr.cyc.org.tw / tp12.aspx?module = login_page & files = login