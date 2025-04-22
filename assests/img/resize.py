from PIL import Image

def rotate_and_resize_image(image_path, output_path, new_width, new_height):
    """
    Rotates a PNG image by 90 degrees clockwise and resizes it.

    Args:
        image_path (str): The path to the input PNG image.
        output_path (str): The path to save the rotated and resized image.
        new_width (int): The desired width of the output image.
        new_height (int): The desired height of the output image.
    """
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Rotate the image by 90 degrees clockwise
        rotated_img = img.rotate(-90, expand=True) # Use -90 for clockwise

        # Resize the image
        resized_img = rotated_img.resize((new_width, new_height))

        # Save the rotated and resized image, preserving PNG format
        resized_img.save(output_path, "PNG")

        print(f"Image successfully rotated and resized. Saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    image_file = "input.png"  # Replace with your input PNG image path
    output_file = "output.png" # Replace with your desired output path
    new_width = 800
    new_height = 750

    # Create a dummy input.png if it does not exist
    try:
        with open(image_file, "wb") as f:
            # Create a minimal PNG file (8x8 pixels, black, no compression)
            minimal_png_data = bytes([
                137, 80, 78, 71, 13, 10, 26, 10,  # PNG signature
                0, 0, 0, 13,             # IHDR chunk start
                73, 72, 68, 82,             # IHDR chunk type
                0, 0, 0, 8,                # Width: 8 pixels
                0, 0, 0, 8,                # Height: 8 pixels
                8,                       # Bit depth: 8
                0,                       # Color type: 0 (Grayscale)
                0,                       # Compression method: 0 (deflate)
                0,                       # Filter method: 0 (adaptive)
                0,                       # Interlace method: 0 (none)
                121, 212, 125, 114,       # CRC for IHDR chunk
                0, 0, 0, 1,              # IDAT chunk start
                73, 68, 65, 84,             # IDAT chunk type
                120, 156,                 #Deflate, no compression
                0,                        # data
                2, 254,                   # adler32
                0, 0, 0, 0,              # IEND chunk start
                73, 69, 78, 68,             # IEND chunk type
                174, 66, 96, 130          # CRC for IEND chunk
            ])
            f.write(minimal_png_data)
    except FileExistsError:
        pass # If the file already exists, we do nothing

    rotate_and_resize_image('background.png', output_file, new_width, new_height)
