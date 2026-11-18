\# Smart Wardrobe AI



An IoT-powered clothing recommendation system using Raspberry Pi 5, computer vision, local AI, and Microsoft Azure.



\## Project Overview



Smart Wardrobe AI analyzes clothing items and determines whether they are suitable for the current temperature.



The system captures an image using a Raspberry Pi Camera Module or accepts an existing photograph. A TMP102 sensor measures the ambient temperature, while an Ollama vision model identifies the clothing and generates a recommendation.



The results, including the photograph, temperature, and AI analysis, are uploaded to Microsoft Azure and displayed through a Streamlit dashboard.



\## Features



\- Capture clothing images using Picamera2

\- Analyze existing JPG and PNG images

\- Measure temperature using a TMP102 sensor

\- Identify clothing using Ollama and Gemma 3

\- Recommend clothing based on ambient temperature

\- Save photographs to Azure Blob Storage

\- Store sensor readings and recommendations in Azure Table Storage

\- View previous scans through a Streamlit dashboard



\## Technologies Used



| Technology | Purpose |

|---|---|

| Raspberry Pi 5 | Main IoT computing device |

| Picamera2 | Camera image capture |

| TMP102 | Ambient temperature sensing |

| Python | Application development |

| Ollama / Gemma 3 4B | Local AI image analysis |

| Azure Blob Storage | Photograph storage |

| Azure Table Storage | Sensor and AI-result storage |

| Streamlit | Web dashboard |



\## Hardware Requirements



\- Raspberry Pi 5 (8 GB recommended)

\- Raspberry Pi Camera Module

\- TMP102 temperature sensor

\- Jumper wires

\- Power supply

\- Internet connection for Azure uploads



\## TMP102 Connections



| TMP102 | Raspberry Pi |

|---|---|

| VCC | 3.3V (Pin 1) |

| GND | GND (Pin 6) |

| SDA | GPIO 2 (Pin 3) |

| SCL | GPIO 3 (Pin 5) |



The TMP102 commonly uses I²C address `0x48`. Depending on the ADD0 connection, it may use another supported address.



\## Installation



\### 1. Download the project



Clone the repository:



```bash

git clone https://github.com/YOUR\_USERNAME/smart-wardrobe-ai.git

cd smart-wardrobe-ai

```



Alternatively, click \*\*Code → Download ZIP\*\* on GitHub.



\### 2. Configure the Raspberry Pi



Enable I²C:



```bash

sudo raspi-config

```



Select \*\*Interface Options → I2C → Enable\*\*.



Install camera and Python dependencies:



```bash

sudo apt update

sudo apt install -y python3-venv python3-picamera2 i2c-tools

```



Create a virtual environment in the Raspberry Pi application directory:



```bash

python3 -m venv --system-site-packages .venv

source .venv/bin/activate

```



Install the Python packages:



```bash

python -m pip install ollama smbus2 tinydb azure-storage-blob azure-data-tables python-dotenv

```



\### 3. Install Ollama



Follow the installation instructions at https://ollama.com/download/linux.



Download the vision model:



```bash

ollama pull gemma3:4b

```



\### 4. Configure Azure Storage



Create an Azure Storage account with:



\- A Blob container named `clothing-images`

\- A Table named `ClothingReadings`



Create a `.env` file in the application's working directory:



```dotenv

AZURE\_STORAGE\_CONNECTION\_STRING="YOUR\_CONNECTION\_STRING"

```



Keep the connection string private.



\### 5. Run the clothing AI



Navigate to the directory containing `clothing\_ai.py` and run:



```bash

python clothing\_ai.py

```



Choose whether to capture a photograph using Picamera2 or analyze an existing image.



The application measures the temperature, generates a recommendation, and uploads its results to Azure.



\## Running the Streamlit Dashboard



On a Windows or Linux computer, navigate to the directory containing `dashboard.py`.



Create a Python virtual environment and install:



```bash

python -m pip install streamlit pandas azure-data-tables azure-storage-blob python-dotenv

```



Configure the same Azure Storage connection string in a local `.env` file.



Run:



```bash

python -m streamlit run dashboard.py

```



Open http://localhost:8501 in your browser.



The dashboard displays captured images, temperatures, AI recommendations, and previous scan history.



\## System Architecture



```text

Raspberry Pi 5

&#x20;   |

&#x20;   +-- Picamera2 → Clothing photograph

&#x20;   |

&#x20;   +-- TMP102 → Ambient temperature

&#x20;   |

&#x20;   v

Ollama Vision AI (Gemma 3)

&#x20;   |

&#x20;   v

Clothing Recommendation

&#x20;   |

&#x20;   +-- Azure Blob Storage → Photographs

&#x20;   |

&#x20;   +-- Azure Table Storage → Analysis and sensor data

&#x20;                                 |

&#x20;                                 v

&#x20;                          Streamlit Dashboard

```



\## Limitations



\- AI inference may be slow when running directly on the Raspberry Pi CPU.

\- The TMP102 measures local ambient temperature, not necessarily outdoor weather.

\- Clothing recommendations depend on visual interpretation and temperature alone.

\- Azure uploads and the cloud dashboard require internet connectivity.



\## Future Improvements



\- Faster AI models and GPU-assisted inference

\- A publicly hosted dashboard using Azure App Service

\- Automated refresh when new clothing scans are uploaded

\- Clothing categorization and searchable scan history

\- Additional environmental sensors



\## License



No open-source license has been selected.

