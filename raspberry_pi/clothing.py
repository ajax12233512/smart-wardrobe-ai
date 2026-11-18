from pathlib import Path
from azure_upload import upload_clothing_result
from pathlib import Path
from datetime import datetime
from smbus2 import SMBus
from ollama import chat

from picamera2 import Picamera2
import time
from pathlib import Path

IMAGE_PATH = Path("clothing.jpg")

MODEL = "gemma3:4b"
ADDRESSES = [0x48, 0x49]
IMAGE_PATH = Path("clothing.jpg")


def read_temperature():
    """Read TMP102, trying both possible addresses."""
    with SMBus(1) as bus:
        for address in ADDRESSES:
            try:
                data = bus.read_i2c_block_data(
                    address, 0x00, 2
                )

                # TMP102 normal 12-bit mode
                raw = (data[0] << 4) | (data[1] >> 4)

                if raw & 0x800:
                    raw -= 4096

                celsius = raw * 0.0625
                fahrenheit = celsius * 9 / 5 + 32

                print(f"TMP102 detected at {hex(address)}")

                return celsius, fahrenheit

            except OSError:
                continue

    raise RuntimeError(
        "TMP102 not responding at 0x48 or 0x49"
    )


def take_picture():
    """Capture a picture using Raspberry Pi Camera Module."""

    picam2 = Picamera2()

    try:
        config = picam2.create_still_configuration()
        picam2.configure(config)

        picam2.start()

        # Allow automatic exposure and white balance to settle
        time.sleep(2)

        picam2.capture_file(str(IMAGE_PATH))

        if not IMAGE_PATH.exists():
            raise RuntimeError("Picture was not saved.")

        print(f"Picture saved to {IMAGE_PATH.resolve()}")

        return IMAGE_PATH

    finally:
        picam2.stop()
        picam2.close()


def analyze_clothing(image_path, celsius, fahrenheit):
    """Ask Ollama to evaluate clothing from the image."""

    prompt = f"""
You are a helpful clothing and weather assistant.

An image of one clothing item is provided.

The current measured ambient temperature is:
{celsius:.2f} degrees Celsius
{fahrenheit:.2f} degrees Fahrenheit

Your tasks:

1. Identify the main clothing item in the image.
2. Describe its visible color and style.
3. Estimate whether it appears lightweight,
   medium-weight, or heavyweight.
4. Decide whether it is suitable for the
   measured temperature.
5. Explain your reasoning briefly.

Do not invent a temperature reading.
Do not claim you know the exact fabric or
thickness unless it is clearly identifiable.
If uncertain, say so.

Use this format:

Clothing:
Description:
Temperature:
Recommendation:
Reason:
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [str(image_path)]
            }
        ]
    )

    return response.message.content


def select_image():
    """Let the user take a photo or choose an existing one."""

    while True:
        print("\n=== Image Selection ===")
        print("1. Take a new picture")
        print("2. Use an existing picture")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            print("\nStarting Raspberry Pi camera...")
            input("Place clothing in front of camera, then press Enter.")

            return take_picture()

        elif choice == "2":
            while True:
                path_input = input(
                    "\nEnter the image path (or 'back'): "
                ).strip().strip('"').strip("'")

                if path_input.lower() == "back":
                    break

                image_path = Path(path_input).expanduser()

                if not image_path.is_file():
                    print("File not found. Try again.")
                    continue

                if image_path.suffix.lower() not in (
                    ".jpg", ".jpeg", ".png"
                ):
                    print("Please select a JPG or PNG image.")
                    continue

                print(f"Selected image: {image_path.resolve()}")
                return image_path.resolve()

        elif choice == "3":
            return None

        else:
            print("Invalid option. Please select 1, 2, or 3.")




def main():
    print("=== AI Clothing Assistant ===")

    # STEP 1: Select image source
    image_path = select_image()

    if image_path is None:
        print("Exiting AI Clothing Assistant.")
        return

    # STEP 2: Read current TMP102 temperature
    celsius, fahrenheit = read_temperature()

    print(f"\nCurrent Temperature: {fahrenheit:.2f} F")

    # STEP 3: Analyze the selected image using Ollama
    print("\nAnalyzing clothing...")

    result = analyze_clothing(
        image_path,
        celsius,
        fahrenheit
    )

    print("\n=== AI Recommendation ===")
    print(result)

    # STEP 4: Upload selected image and results to Azure
    print("\n=== Azure Upload ===")

    try:
        upload_info = upload_clothing_result(
            image_path=image_path,
            celsius=celsius,
            fahrenheit=fahrenheit,
            ai_result=result
        )

        print("Azure upload successful!")
        print("Scan ID:", upload_info["scan_id"])

    except Exception as e:
        print("Azure upload failed:", e)
        print(
            "Local image and AI result remain available."
        )


if __name__ == "__main__":
    main()
